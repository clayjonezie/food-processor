def parse_and_call(filename, func):
  for line in open(filename):
    vals = line.split('^')
    rm_tild = lambda s : s.replace('~','')
    vals = map(rm_tild, vals)

    # turns the micro symbol into a u
    uni = lambda s : s.replace('\xB5', 'u').decode('utf-8')
    vals = map(uni, vals)
    func(vals)
