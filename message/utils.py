def num (s):
    try:
        return int(s)
    except ValueError:
        return float(s)
    

def uniqify(seq, idfun=None):  
  return list(set(map(idfun, seq)))