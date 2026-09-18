import hashlib
import numpy as np
import pandas as pd

# =============================================================================
# Универсальный бутстрэп-тест по рекламным кампаниям (brcb)
# -----------------------------------------------------------------------------
# Логика:
#   1. df режется по 'brcb' — каждая рекламная кампания тестируется отдельно.
#   2. Внутри кампании тестовая группа всегда 'TG', контроль — все остальные
#      значения 'type_group' (обычно 'GKG', опционально ещё 'LCG'); TG
#      сравнивается с каждой контрольной группой отдельно. Названия контрольных
#      групп нигде не хардкодятся — берётся всё, что не 'TG', поэтому одинаково
#      работает и при двух, и при трёх группах.
#   3. Если в df есть поле 'channel':
#        - TG дополнительно разбивается на подгруппы по 'channel';
#        - контрольные группы НЕ разбиваются по 'channel' (даже если оно у них
#          заполнено) — используются целиком;
#        - каждая channel-подгруппа TG сравнивается с целыми контрольными
#          группами;
#        - помимо этого отдельно считается общий результат по кампании целиком
#          (TG без разбивки по channel vs контроль) — в результатах это строки
#          с channel == 'ALL'.
#   4. Все результаты (по всем brcb и всем срезам channel) собираются в одну
#      таблицу results_df — её и будем экспортировать в excel на следующем шаге.
#
# Допущение (не было явно оговорено, поправь если не так): строки TG, у которых
# 'channel' не заполнен (NaN), не попадают ни в одну channel-подгруппу, но
# участвуют в общем расчёте (channel == 'ALL'), т.к. он не фильтрует по channel.
# =============================================================================

# ---------------------------- настройки ----------------------------
N_BOOT = 2000               # число бутстрэп-итераций
ALPHA = 0.05                 # уровень значимости
BASE_SEED = 42                # базовый сид
MIN_GROUP_SIZE = 1           # минимальный размер группы (после dropna по targer),
                              # при котором тест вообще считаем; сейчас отсекает
                              # только полностью пустые группы — подними значение,
                              # если нужно отсекать нестабильные маленькие выборки
BOOT_CHUNK = 200             # чанк бутстрэп-итераций (ограничение по памяти)
TEST_GROUP = 'TG'            # название тестовой группы


# ---------------------------- бутстрэп ----------------------------

def _stable_seed(*parts) -> int:
    """
    Детерминированный int-сид из ключа сегмента (brcb, channel, группа и т.п.),
    не зависящий от PYTHONHASHSEED и от порядка обхода групп/словарей.
    """
    s = '|'.join(map(str, parts))
    return int(hashlib.sha256(s.encode()).hexdigest()[:12], 16)


def poisson_bootstrap_mean(x, seed_parts, n_boot=N_BOOT, chunk=BOOT_CHUNK):
    """Пуассон-бутстрэп распределения среднего (векторизовано, чанками по памяти)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    rng = np.random.default_rng(np.random.SeedSequence([BASE_SEED, _stable_seed(*seed_parts)]))
    means = np.empty(n_boot)
    for start in range(0, n_boot, chunk):
        end = min(start + chunk, n_boot)
        w = rng.poisson(1, size=(end - start, n))    # веса ~ Poisson(1), матрица (batch x n)
        means[start:end] = (w @ x) / w.sum(axis=1)   # взвешенное среднее на каждой итерации
    return means


def compare(name_c, x_c, boot_c, name_t, x_t, boot_t, alpha=ALPHA, verbose=False):
    """Сравнение теста с контролем по бутстрэп-распределениям средних."""
    diff = boot_t - boot_c
    obs_diff = x_t.mean() - x_c.mean()
    lo, hi = np.percentile(diff, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    p_value = min(2 * min((diff <= 0).mean(), (diff >= 0).mean()), 1.0)
    uplift = obs_diff / x_c.mean() * 100 if x_c.mean() != 0 else np.nan

    row = dict(
        control=name_c, test=name_t,
        n_control=len(x_c), mean_control=x_c.mean(),
        n_test=len(x_t), mean_test=x_t.mean(),
        obs_diff=obs_diff, ci_low=lo, ci_high=hi,
        uplift_pct=uplift, p_value=p_value,
        significant=p_value < alpha,
    )
    if verbose:
        print(f'--- {name_t} vs {name_c} ---')
        print(f'n_{name_c}={len(x_c)}, mean={x_c.mean():.2f}; '
              f'n_{name_t}={len(x_t)}, mean={x_t.mean():.2f}')
        print(f'Разница: {obs_diff:.2f}, {int((1 - alpha) * 100)}% ДИ: [{lo:.2f}, {hi:.2f}], '
              f'uplift: {uplift:.2f}%, p-value: {p_value:.4f}',
              '-> значимо' if row['significant'] else '-> не значимо', '\n')
    return row


# ---------------------------- подготовка одной группы ----------------------------

def _bootstrap_stats(sub, metric_col, id_col, seed_parts, min_n=MIN_GROUP_SIZE, n_boot=N_BOOT):
    """
    sub — уже отфильтрованный срез (одна группа/канал внутри одной кампании).
    Возвращает (x, boot, reason): reason не None, если тест посчитать не удалось.
    """
    if id_col in sub.columns:
        dup = sub[id_col].duplicated().sum()
        if dup > 0:
            print(f'[предупреждение] {seed_parts}: {dup} дублей по "{id_col}" '
                  f'— ожидалась агрегация до одного значения на пользователя')

    x = sub[metric_col].dropna().to_numpy(float)
    if len(x) < min_n:
        return None, None, f'мало данных (n={len(x)})'
    boot = poisson_bootstrap_mean(x, seed_parts=seed_parts, n_boot=n_boot)
    return x, boot, None


def _compare_tg_vs_controls(tg_stats, control_data, brcb_val, channel_val, alpha, verbose):
    x_t, boot_t, reason_t = tg_stats
    rows = []
    if x_t is None:
        for g in control_data:
            rows.append(dict(brcb=brcb_val, channel=channel_val, control=g, test=TEST_GROUP,
                              status=f'{TEST_GROUP}: {reason_t}'))
        return rows

    for g, (x_c, boot_c, reason_c) in control_data.items():
        if x_c is None:
            rows.append(dict(brcb=brcb_val, channel=channel_val, control=g, test=TEST_GROUP,
                              status=f'{g}: {reason_c}'))
            continue
        row = compare(g, x_c, boot_c, TEST_GROUP, x_t, boot_t, alpha=alpha, verbose=verbose)
        row.update(brcb=brcb_val, channel=channel_val, status='ok')
        rows.append(row)
    return rows


# ---------------------------- одна кампания (brcb) ----------------------------

def run_brcb_tests(df_brcb, brcb_val, group_col, metric_col, id_col, channel_col=None,
                    n_boot=N_BOOT, alpha=ALPHA, verbose=False):
    groups_present = df_brcb[group_col].dropna().unique().tolist()

    if TEST_GROUP not in groups_present:
        return [dict(brcb=brcb_val, channel='ALL', control=None, test=TEST_GROUP,
                      status=f'нет группы {TEST_GROUP}')]

    controls = [g for g in groups_present if g != TEST_GROUP]
    if not controls:
        return [dict(brcb=brcb_val, channel='ALL', control=None, test=TEST_GROUP,
                      status='нет контрольных групп')]

    # контроль считаем целиком, один раз на кампанию — по channel не режем
    control_data = {
        g: _bootstrap_stats(df_brcb.loc[df_brcb[group_col] == g], metric_col, id_col,
                             seed_parts=(brcb_val, g), n_boot=n_boot)
        for g in controls
    }

    rows = []

    # общий результат по кампании целиком, без разбивки по channel
    tg_all = _bootstrap_stats(df_brcb.loc[df_brcb[group_col] == TEST_GROUP], metric_col, id_col,
                               seed_parts=(brcb_val, TEST_GROUP), n_boot=n_boot)
    rows += _compare_tg_vs_controls(tg_all, control_data, brcb_val, 'ALL', alpha, verbose)

    # разбивка TG по channel (контроль остаётся целым)
    if channel_col is not None and channel_col in df_brcb.columns:
        tg_mask = df_brcb[group_col] == TEST_GROUP
        channels = df_brcb.loc[tg_mask, channel_col].dropna().unique().tolist()
        for ch in channels:
            sub_t_ch = df_brcb.loc[tg_mask & (df_brcb[channel_col] == ch)]
            tg_ch = _bootstrap_stats(sub_t_ch, metric_col, id_col,
                                      seed_parts=(brcb_val, TEST_GROUP, ch), n_boot=n_boot)
            rows += _compare_tg_vs_controls(tg_ch, control_data, brcb_val, ch, alpha, verbose)

    return rows


# ---------------------------- поправка Холма ----------------------------

def _holm_adjust(pvals):
    pvals = np.asarray(pvals, dtype=float)
    m = len(pvals)
    order = np.argsort(pvals)
    ranked = pvals[order]
    adj = np.empty(m)
    running_max = 0.0
    for i in range(m):
        running_max = max(running_max, (m - i) * ranked[i])
        adj[i] = min(running_max, 1.0)
    out = np.empty(m)
    out[order] = adj
    return out


def _add_holm_correction(results_df, family_col='brcb'):
    """Поправка Холма на множественные сравнения — отдельно внутри каждого brcb."""
    results_df = results_df.copy()
    results_df['p_value_holm'] = np.nan
    ok = results_df['status'] == 'ok'
    for _, idx in results_df.loc[ok].groupby(family_col).groups.items():
        results_df.loc[idx, 'p_value_holm'] = _holm_adjust(results_df.loc[idx, 'p_value'].to_numpy())
    return results_df


# ---------------------------- весь df ----------------------------

def run_all_tests(df, brcb_col='brcb', group_col='type_group', metric_col='targer',
                   id_col='ybpideal', channel_col='channel', n_boot=N_BOOT, alpha=ALPHA,
                   verbose=False, holm_correction=True):
    has_channel = channel_col is not None and channel_col in df.columns

    all_rows = []
    for brcb_val in df[brcb_col].dropna().unique():
        df_brcb = df.loc[df[brcb_col] == brcb_val]
        all_rows += run_brcb_tests(df_brcb, brcb_val, group_col, metric_col, id_col,
                                    channel_col=channel_col if has_channel else None,
                                    n_boot=n_boot, alpha=alpha, verbose=verbose)

    results_df = pd.DataFrame(all_rows)

    cols_order = ['brcb', 'channel', 'control', 'test', 'n_control', 'mean_control',
                  'n_test', 'mean_test', 'obs_diff', 'ci_low', 'ci_high', 'uplift_pct',
                  'p_value', 'significant', 'status']
    cols_order = [c for c in cols_order if c in results_df.columns]
    results_df = results_df[cols_order + [c for c in results_df.columns if c not in cols_order]]

    if holm_correction and 'p_value' in results_df.columns:
        results_df = _add_holm_correction(results_df, family_col=brcb_col)

    return results_df


# ------------------------------- пример запуска -------------------------------
# results_df = run_all_tests(df)
# results_df
