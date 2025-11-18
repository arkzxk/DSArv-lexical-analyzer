import dsarv

while True:
  text = input('DSArv > ')
  result, error = dsarv.run('<stdin>', text)

  if error: print(error.as_string())
  else: print(result)