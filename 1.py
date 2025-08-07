import pandas as pd
data = [
    {'id': 1, 'name': 'Joe'},
    {'id': 2, 'name': 'Henry'},
    {'id': 3, 'name': 'Sam'},
    {'id': 4, 'name': 'Max'}
]
customers = pd.DataFrame(data)
customers.head()