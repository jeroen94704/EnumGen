import enumgen

enumgen.define('colorapp', 'Color', [
    ('RED'      , 'Red'),
    ('GREEN'    , 'Green'),
    ('BLUE'     , 'Blue'),
    ('YELLOW'   , 'Yellow'),
    ])

if __name__ == '__main__':
    enumgen.write('output', 'example.py')

