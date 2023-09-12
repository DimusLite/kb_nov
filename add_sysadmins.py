import r_scrap

users = [(0, 'Лёгкий Дмитрий Сергеевич', 'Lite', '',
          'u=%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98%D0%BB%D1%8C%D1'
          '%8F%20%D0%92%D0%B0%D0%B4%D0%B8%D0%BC%D0%BE%D0%B2%D0%B8%D1%87'
          '%7C%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98%D0%BB%D1%8C'
          '%D1%8F%20%D0%92%D0%B0%D0%B4%D0%B8%D0%BC%D0%BE%D0%B2%D0%B8%D1%'
          '87%7C%D0%9F%D0%BE%D0%BF%D0%BE%D0%B2%20%D0%95%D0%B2%D0%B3%D0%B5'
          '%D0%BD%D0%B8%D0%B9%20%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0'
          '%B5%D0%B2%D0%B8%D1%87%7C%D0%9B%D1%91%D0%B3%D0%BA%D0%B8%D0%B9'
          '%20%D0%94%D0%BC%D0%B8%D1%82%D1%80%D0%B8%D0%B9%20%D0%A1%D0%B5'
          '%D1%80%D0%B3%D0%B5%D0%B5%D0%B2%D0%B8%D1%87; r_modul=summary;'),
         (1, 'Галаша Александр Александрович', 'Galasha',
          '&user=36c5b421216cd156fd18f7b866354a16',
          'u=%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98%D0%BB%D1%8C%D1'
          '%8F%20%D0%92%D0%B0%D0%B4%D0%B8%D0%BC%D0%BE%D0%B2%D0%B8%D1%87%7C'
          '%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98.%D0%92%2C%7C%D0%9F'
          '%D0%BE%D0%BF%D0%BE%D0%B2%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8'
          '%D0%B9%20%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0%B5%D0%B2%D0%B8'
          '%D1%87%7C%D0%93%D0%B0%D0%BB%D0%B0%D1%88%D0%B0%20%D0%90%D0%BB%D0'
          '%B5%D0%BA%D1%81%D0%B0%D0%BD%D0%B4%D1%80%20%D0%90%D0%BB%D0%B5%D0'
          '%BA%D1%81%D0%B0%D0%BD%D0%B4%D1%80%D0%BE%D0%B2%D0%B8%D1%87;'
          ' r_modul=summary;'),
         (2, 'Григорьев Александр Владимирович', 'Grigoriev',
          '&user=040d1a1362f3ff3a6746340d578b4672',
          'u=%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98%D0%BB%D1%8C%D1%8F'
          '%20%D0%92%D0%B0%D0%B4%D0%B8%D0%BC%D0%BE%D0%B2%D0%B8%D1%87%7C%D0%93'
          '%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98.%D0%92%2C%7C%D0%9F%D0%BE'
          '%D0%BF%D0%BE%D0%B2%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D0%B9%20'
          '%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0%B5%D0%B2%D0%B8%D1%87%7C%D0'
          '%93%D1%80%D0%B8%D0%B3%D0%BE%D1%80%D1%8C%D0%B5%D0%B2%20%D0%90%D0%BB'
          '%D0%B5%D0%BA%D1%81%D0%B0%D0%BD%D0%B4%D1%80%20%D0%92%D0%BB%D0%B0%D0'
          '%B4%D0%B8%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B8%D1%87;'
          ' r_modul=summary;'),
         (3, 'Пинчук Алексей Анатольевич', 'Pinchuk',
          '&user=ce1835257ace0ad250d33b41cf0190eb',
          'u=%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98%D0%BB%D1%8C%D1%8F'
          '%20%D0%92%D0%B0%D0%B4%D0%B8%D0%BC%D0%BE%D0%B2%D0%B8%D1%87%7C%D0%93'
          '%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98.%D0%92%2C%7C%D0%9F%D0%BE'
          '%D0%BF%D0%BE%D0%B2%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D0%B9%20'
          '%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0%B5%D0%B2%D0%B8%D1%87%7C%D0'
          '%9F%D0%B8%D0%BD%D1%87%D1%83%D0%BA%20%D0%90%D0%BB%D0%B5%D0%BA%D1%81'
          '%D0%B5%D0%B9%20%D0%90%D0%BD%D0%B0%D1%82%D0%BE%D0%BB%D1%8C%D0%B5%D0'
          '%B2%D0%B8%D1%87; r_modul=summary;')
]
print(r_scrap.upsert_db_users(users))