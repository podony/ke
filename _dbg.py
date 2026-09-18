import re
cc = open(chr(99)+chr(111)+chr(109)+chr(109)+chr(111)+chr(110)+chr(47)+chr(112)+chr(97)+chr(114)+chr(97)+chr(109)+chr(115)+chr(46)+chr(99)+chr(99), encoding=chr(117)+chr(116)+chr(102)+chr(45)+chr(56)).read()
pat = re.compile(chr(92)+chr(123)+chr(34)+chr(40)+chr(92)+chr(93)+chr(34)+chr(43)+chr(41)+chr(34)+chr(44)+chr(92)+chr(115)+chr(42)+chr(40)+chr(80)+chr(69)+chr(82)+chr(83)+chr(73)+chr(83)+chr(84)+chr(69)+chr(78)+chr(84)+chr(124)+chr(67)+chr(76)+chr(69)+chr(65)+chr(82)+chr(95)+chr(79)+chr(78)+chr(95)+chr(92)+chr(119)+chr(43)+chr(124)+chr(65)+chr(76)+chr(76)+chr(41)+chr(92)+chr(125)+chr(125))
print(pat.pattern)
pairs = pat.findall(cc)
keys = [a for a,b in pairs]
print(chr(107)+chr(101)+chr(121)+chr(115), len(keys))
