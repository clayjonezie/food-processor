def parse_and_call(filename, func):
  for line in open(filename):
    vals = line.split('^')
    rm_tild = lambda s : s.replace('~','')
    vals = map(rm_tild, vals)

    uni = lambda s : unicode(s)
    vals = map(uni, vals)
    print vals
    func(vals)
