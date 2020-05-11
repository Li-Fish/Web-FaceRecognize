import os
print(os.path.exists('123/123/123'))
if not os.path.exists('123/123/123'):
    os.mkdir('123/123/123')