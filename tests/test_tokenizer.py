import unittest

from scrappybara.preprocessing.tokenizer import Tokenizer

_TOKENIZE = Tokenizer()


def _tokenize(text):
    return ' '.join([str(token) for token in _TOKENIZE(text)])


class TestTokenizer(unittest.TestCase):

    # BLOCKS
    # -------------------------------------------------------------------------->

    def test_indirect_speech_blocks(self):
        self.assertEqual('Well , he said ༺1༻', _tokenize('Well, he said ༺1༻'))
        self.assertEqual('⦅1⦆ Well , he said ༺1༻', _tokenize('⦅1⦆ Well, he said ༺1༻'))

    # SHORT TEXT
    # -------------------------------------------------------------------------->

    def test_split_special_words(self):
        self.assertEqual('I can not do that .', _tokenize('I cannot do that.'))
        self.assertEqual('Can not do that !', _tokenize('Cannot do that!'))

    def test_links(self):
        self.assertEqual('domain.com', _tokenize('domain.com'))
        self.assertEqual('Cellucor.com', _tokenize('Cellucor.com'))
        self.assertEqual('DOMAIN.COM', _tokenize('DOMAIN.COM'))
        self.assertEqual('sub.domain.com.au', _tokenize('sub.domain.com.au'))
        self.assertEqual('sub.domain123.com.au', _tokenize('sub.domain123.com.au'))
        self.assertEqual('data@unicef.org.au', _tokenize('data@unicef.org.au'))
        self.assertEqual('mr.aid@unicef21.org.au', _tokenize('mr.aid@unicef21.org.au'))
        self.assertEqual('tacos.pic.twitter.com/Q4usgzGMHq', _tokenize('tacos.pic.twitter.com/Q4usgzGMHq'))

    def test_dots_single_tokens_nosplit(self):
        self.assertEqual('a.', _tokenize('a.'))
        self.assertEqual('.end', _tokenize('.end'))
        self.assertEqual('.End', _tokenize('.End'))
        self.assertEqual('1 .', _tokenize('1.'))
        self.assertEqual('.11', _tokenize('.11'))
        self.assertEqual('1.deliver', _tokenize('1.deliver'))
        self.assertEqual('1.Deliver', _tokenize('1.Deliver'))
        self.assertEqual('deliver.1', _tokenize('deliver.1'))
        self.assertEqual('deliveR.1', _tokenize('deliveR.1'))
        self.assertEqual('.deliver', _tokenize('.deliver'))
        self.assertEqual('.Deliver', _tokenize('.Deliver'))
        self.assertEqual('aaa.deliver', _tokenize('aaa.deliver'))
        self.assertEqual('aaA.Deliver', _tokenize('aaA.Deliver'))
        self.assertEqual('$1.3M', _tokenize('$1.3M'))
        self.assertEqual('1.1', _tokenize('1.1'))
        self.assertEqual('123.123', _tokenize('123.123'))
        self.assertEqual('123.123.1', _tokenize('123.123.1'))
        self.assertEqual('1.1.1.1', _tokenize('1.1.1.1'))
        self.assertEqual('A.B.1.C', _tokenize('A.B.1.C'))
        self.assertEqual('A.B.C', _tokenize('A.B.C'))
        self.assertEqual('A.B.C.', _tokenize('A.B.C.'))
        self.assertEqual('e.g.', _tokenize('e.g.'))
        self.assertEqual('e.g', _tokenize('e.g'))
        self.assertEqual('A.A', _tokenize('A.A'))
        self.assertEqual('U.S.', _tokenize('U.S.'))
        self.assertEqual('u.s.', _tokenize('u.s.'))
        self.assertEqual('1.A', _tokenize('1.A'))
        self.assertEqual('A.1', _tokenize('A.1'))
        self.assertEqual('I1.I0I', _tokenize('I1.I0I'))
        self.assertEqual('items.101', _tokenize('items.101'))
        self.assertEqual('items.I0I.A', _tokenize('items.I0I.A'))

    def test_multiple_dots_split(self):
        self.assertEqual('a new ... Sentence', _tokenize('a new... Sentence'))
        self.assertEqual('bla ...', _tokenize('bla...'))

    def test_multiple_sentence_enders(self):
        self.assertEqual('a new !!! Sentence', _tokenize('a new!!! Sentence'))
        self.assertEqual('a new ?? Sentence', _tokenize('a new?? Sentence'))
        self.assertEqual('a new ??! Sentence', _tokenize('a new??! Sentence'))

    def test_dots_split(self):
        self.assertEqual('a new . Sentence', _tokenize('a new.Sentence'))
        self.assertEqual('December 4 . Sentence', _tokenize('December 4. Sentence'))
        self.assertEqual('try mindfulchef.com . And this .', _tokenize('try mindfulchef.com. And this.'))
        self.assertEqual('a new . Sentence', _tokenize('a new. Sentence'))
        self.assertEqual('Fine Arts . She', _tokenize('Fine Arts. She'))
        self.assertEqual('in june 1962 . Blabla', _tokenize('in june 1962. Blabla'))
        self.assertEqual('information etc . SVN , NN', _tokenize('information etc. SVN, NN'))

    def test_dots_nosplit(self):
        self.assertEqual('use .NET', _tokenize('use .NET'))
        self.assertEqual('a new.sentence', _tokenize('a new.sentence'))
        self.assertEqual('a new .sentence', _tokenize('a new .sentence'))
        self.assertEqual('a new. sentence', _tokenize('a new. sentence'))
        self.assertEqual('market in 2015. includes', _tokenize('market in 2015. includes'))
        self.assertEqual('the 69th regt. ,', _tokenize('the 69th regt.,'))
        self.assertEqual('the 69th regt. :', _tokenize('the 69th regt.:'))
        self.assertEqual('the 69th regt. ;', _tokenize('the 69th regt.;'))
        self.assertEqual('the 69th regt . )', _tokenize('the 69th regt.)'))
        self.assertEqual('a srgt . ( born )', _tokenize('a srgt. (born)'))
        self.assertEqual('4. bought', _tokenize('4. bought'))
        self.assertEqual('4 . I bought', _tokenize('4. I bought'))
        self.assertEqual('A. I bought', _tokenize('A. I bought'))
        self.assertEqual('A. I bought A. I bought', _tokenize('A. I bought A. I bought'))
        self.assertEqual('1.A. I bought', _tokenize('1.A. I bought'))
        self.assertEqual('1.A I bought', _tokenize('1.A I bought'))
        self.assertEqual('( 1 . Todo Cambia )', _tokenize('(1. Todo Cambia)'))
        self.assertEqual('( 1. todo )', _tokenize('(1. todo)'))
        self.assertEqual('manuf. comm. strategies', _tokenize('manuf. comm. strategies'))
        self.assertEqual('tech ASP .NET', _tokenize('tech ASP .NET'))
        self.assertEqual('items is N. shore', _tokenize('items is N. shore'))
        self.assertEqual('his name is A. Gray', _tokenize('his name is A. Gray'))
        self.assertEqual('his name is a. gray', _tokenize('his name is a. gray'))
        self.assertEqual('Engage U.S. donors', _tokenize('Engage U.S. donors'))
        self.assertEqual('the min. is 3', _tokenize('the min. is 3'))
        self.assertEqual('the Bld. is', _tokenize('the Bld. is'))
        self.assertEqual('the BLD. is', _tokenize('the BLD. is'))
        self.assertEqual('he is dr. Robin', _tokenize('he is dr. Robin'))
        self.assertEqual('Dr. Robin', _tokenize('Dr. Robin'))
        self.assertEqual('13th ed. New York', _tokenize('13th ed. New York'))
        self.assertEqual('he is Sr. Programmer', _tokenize('he is Sr. Programmer'))
        self.assertEqual('bullet 1. do this', _tokenize('bullet 1. do this'))
        self.assertEqual('bullet 01. do this', _tokenize('bullet 01. do this'))
        self.assertEqual('bullet.2 do this', _tokenize('bullet.2 do this'))
        self.assertEqual('of .20 inch', _tokenize('of .20 inch'))
        self.assertEqual('a. b. (', _tokenize('a. b. ('))
        self.assertEqual('an n. g. :', _tokenize('an n. g. :'))
        self.assertEqual('in u.s. !', _tokenize('in u.s. !'))
        self.assertEqual(', vols. :', _tokenize(', vols. :'))
        self.assertEqual('a volume . "', _tokenize('a volume. "'))
        self.assertEqual("a volume . '", _tokenize("a volume. '"))
        self.assertEqual('a volume . (', _tokenize('a volume. ('))
        self.assertEqual('a volume . )', _tokenize('a volume. )'))
        self.assertEqual('a volume . [', _tokenize('a volume. ['))
        self.assertEqual('a volume . ]', _tokenize('a volume. ]'))
        self.assertEqual('a volume . {', _tokenize('a volume. {'))
        self.assertEqual('a volume . }', _tokenize('a volume. }'))
        self.assertEqual('a volume . |', _tokenize('a volume. |'))
        self.assertEqual('a volume . *', _tokenize('a volume. *'))

    def test_exclamation_points_split(self):
        self.assertEqual('this is you ! Omg', _tokenize('this is you! Omg'))
        self.assertEqual('this is you !', _tokenize('this is you!'))
        self.assertEqual('this is you !!!', _tokenize('this is you!!!'))
        self.assertEqual('my man ! - marcus', _tokenize('my man! - marcus'))

    def test_exclamation_points_nosplit(self):
        self.assertEqual('innovate ! project', _tokenize('innovate! project'))

    def test_non_ambiguous_seperators(self):
        self.assertEqual('this [ is ] you', _tokenize('this [is] you'))
        self.assertEqual('this ( is ) you', _tokenize('this (is) you'))
        self.assertEqual('this { is } you', _tokenize('this {is} you'))
        self.assertEqual('this is you ? omg', _tokenize('this is you? omg'))
        self.assertEqual('this is you ???', _tokenize('this is you???'))
        self.assertEqual(r'me \ you', _tokenize(r'me\you'))
        self.assertEqual('me | you', _tokenize('me|you'))
        self.assertEqual('the " cat " jumps', _tokenize('the "cat" jumps'))
        self.assertEqual('the cat ; jumps', _tokenize('the cat; jumps'))
        self.assertEqual('the cat : jumps', _tokenize('the cat: jumps'))
        self.assertEqual('failures : include', _tokenize('failures :include'))
        self.assertEqual('sell > 12', _tokenize('sell >12'))
        self.assertEqual('sell < 12', _tokenize('sell <12'))
        self.assertEqual('ca = breakfast', _tokenize('ca=breakfast'))
        self.assertEqual('targets =', _tokenize('targets='))

    def test_lt_gt(self):
        self.assertEqual('sell <-- 12', _tokenize('sell <-- 12'))  # ??
        self.assertEqual('sell -> 12', _tokenize('sell -> 12'))
        self.assertEqual('This is < me >', _tokenize('This is <me>'))
        self.assertEqual('Sell > 50%', _tokenize('Sell >50%'))
        self.assertEqual('Sell < 50%', _tokenize('Sell <50%'))

    def test_star(self):
        self.assertEqual('discussion * integration', _tokenize('discussion*integration'))
        self.assertEqual('discussion * integration', _tokenize('discussion****integration'))
        self.assertEqual('123*123', _tokenize('123*123'))
        self.assertEqual('123*abc', _tokenize('123*abc'))

    def test_plus(self):
        self.assertEqual('responsibilities + timeline', _tokenize('responsibilities+timeline'))
        self.assertEqual('hagen + greg + kris', _tokenize('hagen+greg+kris'))
        self.assertEqual('LTED + Wifi + BLE + Secret', _tokenize(' LTED+Wifi+BLE+Secret '))
        self.assertEqual('3+ at', _tokenize('3+at'))
        self.assertEqual('312+ at', _tokenize('312+at'))
        self.assertEqual('aa+', _tokenize('aa+'))

    def test_ampercases(self):
        self.assertEqual('new & old', _tokenize('new&old'))
        self.assertEqual('New & Old', _tokenize('New&Old'))
        self.assertEqual('NEW&OLD', _tokenize('NEW&OLD'))
        self.assertEqual('t&cs', _tokenize('t&cs'))
        self.assertEqual('T&CS', _tokenize('T&CS'))
        self.assertEqual('schedule & provide', _tokenize('schedule& provide'))
        self.assertEqual('schedule & provide', _tokenize('schedule& provide'))
        self.assertEqual('invest R&D', _tokenize('invest R&D'))
        self.assertEqual('invest R&D', _tokenize('invest R &D'))
        self.assertEqual('invest R&D', _tokenize('invest R& D'))
        self.assertEqual('invest R&D', _tokenize('invest R & D'))
        self.assertEqual('invest R & 1', _tokenize('invest R &1'))
        self.assertEqual('invest R & DD', _tokenize('invest R& DD'))
        self.assertEqual('R&D lab', _tokenize('R&D lab'))
        self.assertEqual('R&D lab', _tokenize('R& D lab'))
        self.assertEqual('R&D lab', _tokenize('R &D lab'))
        self.assertEqual('R&D lab', _tokenize('R & D lab'))
        self.assertEqual('invest R&D lab', _tokenize('invest R&D lab'))
        self.assertEqual('invest R&D lab', _tokenize('invest R &D lab'))
        self.assertEqual('invest R&D lab', _tokenize('invest R& D lab'))
        self.assertEqual('invest R&D lab', _tokenize('invest R & D lab'))
        self.assertEqual('invest AR&D lab', _tokenize('invest A R & D lab'))
        self.assertEqual('invest R&DA lab', _tokenize('invest R & D A lab'))
        self.assertEqual('invest RR & R2 A lab', _tokenize('invest RR & R2 A lab'))
        self.assertEqual('kitchen & utility', _tokenize('kitchen&utility'))

    def test_slashes(self):
        self.assertEqual('10/10/2010', _tokenize('10/10/2010'))
        self.assertEqual('b2b / b2c', _tokenize('b2b/b2c'))
        self.assertEqual('me / you', _tokenize('me/you'))
        self.assertEqual('me / you', _tokenize('me /you'))
        self.assertEqual('me / you', _tokenize('me/ you'))
        self.assertEqual('/ external', _tokenize('/external'))
        self.assertEqual('p/a', _tokenize('p/a'))
        self.assertEqual('A/B', _tokenize('A/B'))
        self.assertEqual('A/', _tokenize('A/'))
        self.assertEqual('/B', _tokenize('/B'))

    def test_dashes(self):
        self.assertEqual('Mon-Khmer', _tokenize('Mon–Khmer'))
        self.assertEqual('— this', _tokenize('—this'))

    def test_percentage(self):
        self.assertEqual('%12', _tokenize('%12'))
        self.assertEqual('12%', _tokenize('12%'))
        self.assertEqual('% savings', _tokenize('%savings'))
        self.assertEqual('save % savings', _tokenize('save%savings'))

    def test_colon(self):
        self.assertEqual('example : bla', _tokenize('example: bla'))
        self.assertEqual('raise Q1 : Raise 1$', _tokenize('raise Q1: Raise 1$'))
        self.assertEqual('support : revise', _tokenize('support:revise'))
        self.assertEqual('payroll : hr', _tokenize('payroll:hr'))
        self.assertEqual('Support : Revise', _tokenize('Support:Revise'))
        self.assertEqual('re:invent', _tokenize('re:invent'))
        self.assertEqual('conduct 1:1s', _tokenize('conduct 1:1s'))
        self.assertEqual('ISO 123:123', _tokenize('ISO 123:123'))
        self.assertEqual('A:B', _tokenize('A:B'))
        self.assertEqual('step : 703', _tokenize('step:703'))
        self.assertEqual('Sell 12 :', _tokenize('Sell 12:'))
        self.assertEqual('Strategy : HR', _tokenize('Strategy:HR'))
        self.assertEqual('2 : HR', _tokenize('2:HR'))
        self.assertEqual('12243 : engage', _tokenize('12243:engage'))

    def test_arrows(self):
        self.assertEqual('Sell 12->23', _tokenize('Sell 12->23'))
        self.assertEqual('Sell 12 > 23', _tokenize('Sell 12>23'))
        self.assertEqual('a => b', _tokenize('a = > b'))
        self.assertEqual('x >= 12.5', _tokenize(' x > = 12.5'))
        self.assertEqual('x <= 12.5', _tokenize(' x < = 12.5'))

    def test_comas(self):
        self.assertEqual('hello , hi', _tokenize('hello, hi'))
        self.assertEqual('123 , all good', _tokenize('123, all good'))
        self.assertEqual('all good , 123', _tokenize('all good,123'))
        self.assertEqual('123,123', _tokenize('123,123'))

    def test_single_quotes(self):
        self.assertEqual("Rocco 's blob", _tokenize("Rocco 's blob"))
        self.assertEqual("His name is ' Rob ' bob", _tokenize("His name is 'Rob' bob"))
        self.assertEqual("His name is Rob ' bob '", _tokenize("His name is Rob 'bob'"))
        self.assertEqual("launch ' go live ' strategy", _tokenize("launch 'go live'strategy"))
        self.assertEqual("james o'hare", _tokenize("james o'hare"))
        self.assertEqual("' proposal", _tokenize("'proposal"))
        self.assertEqual("Deliver 4ft", _tokenize("Deliver 4'"))
        self.assertEqual('Deliver 4in', _tokenize('Deliver 4"'))
        self.assertEqual('Deliver 4ft4in', _tokenize('Deliver 4\'4"'))
        self.assertEqual("' we will run items again '", _tokenize("'we will run items again'"))
        self.assertEqual("ceo order ' macbook pro '", _tokenize("ceo order 'macbook pro'"))
        self.assertEqual("rock 'n' roll", _tokenize("rock 'n' roll"))
        self.assertEqual("rock 'n roll", _tokenize("rock 'n roll"))
        self.assertEqual("rock n' roll", _tokenize("rock n' roll"))

    def test_clitics(self):
        self.assertEqual("Jane 's blob", _tokenize("Jane's blob"))
        self.assertEqual("sdo 's", _tokenize("sdo's"))
        self.assertEqual("make SOP 's today", _tokenize("make SOP's today"))
        self.assertEqual("I 'd eat", _tokenize("I'd eat"))
        self.assertEqual("I 'm blob", _tokenize("I'm blob"))
        self.assertEqual("They 'll come", _tokenize("They'll come"))
        self.assertEqual("They 're blobs", _tokenize("They're blobs"))
        self.assertEqual("They 've eaten", _tokenize("They've eaten"))
        self.assertEqual("They are n't blobs", _tokenize("They aren't blobs"))
        self.assertEqual("They ca n't blobs", _tokenize("They can't blobs"))
        self.assertEqual("They have n't blobs", _tokenize("They haven't blobs"))
        self.assertEqual("They is n't blobs", _tokenize("They isn't blobs"))
        self.assertEqual('ifp \'s', _tokenize('ifp\'s'))

    def test_multi_special_chars(self):
        self.assertEqual('bla // bla', _tokenize('bla // bla'))
        self.assertEqual('bla {{ bla }}', _tokenize('bla {{bla}}'))
        self.assertEqual('bla {{ bla }}', _tokenize('bla {{bla}}'))

    def test_bullets(self):
        self.assertEqual('year . * introduce', _tokenize('year. *introduce'))
        self.assertEqual('year . - introduce', _tokenize('year. -introduce'))

    def test_special_chars(self):
        self.assertEqual('_tag #MenArePigs', _tokenize('_tag #MenArePigs'))
        self.assertEqual('_tag @MenArePigs', _tokenize('_tag @MenArePigs'))

    def test_protected_patterns(self):
        self.assertEqual('visit http://bla.com.au', _tokenize('visit http://bla.com.au'))
        self.assertEqual('visit https://bla.com.au/', _tokenize('visit https://bla.com.au/'))
        self.assertEqual('visit www.bla.com.au/bla.pdf', _tokenize('visit www.bla.com.au/bla.pdf'))
        self.assertEqual('visit www.Bla.com and www.Bla2.com', _tokenize('visit www.Bla.com and www.Bla2.com'))

    def test_sentence_parts(self):
        self.assertEqual('on Oct. 29 , 2017 .', _tokenize('on Oct. 29, 2017.'))
        self.assertEqual('involve the U.S. ?', _tokenize('involve the U.S.?'))
        self.assertEqual('" Jump " , he said .', _tokenize('"Jump", he said.'))
        self.assertEqual('" Jump . " , he said .', _tokenize('"Jump.", he said.'))
        self.assertEqual('" Jump . " he said .', _tokenize('"Jump." he said.'))

    def test_multi_dots(self):
        self.assertEqual('Ms. Dean .', _tokenize('Ms. Dean.'))
        self.assertEqual('Ms. Dean . Mrs Dean .', _tokenize('Ms. Dean. Mrs Dean.'))
        self.assertEqual('Sgt. Pepp. went there', _tokenize('Sgt. Pepp. went there'))

    def test_smileys(self):
        self.assertEqual(':-)', _tokenize(':-)'))

    # LONG TEXT
    # -------------------------------------------------------------------------->

    def test_text_1(self):
        self.assertEqual('said Lt. Gov. Brian Calley in a Dec. 19 press release .',
                         _tokenize('said Lt. Gov. Brian Calley in a Dec. 19 press release.'))

    def test_text_2(self):
        self.assertEqual('headquarters in Ghent , Belgium . The company develops',
                         _tokenize('headquarters in Ghent, Belgium. The company develops'))

    def test_text_3(self):
        self.assertEqual('The fastest in the world , by a long margin . Concentrate . Got a picture in mind ?',
                         _tokenize('The fastest in the world, by a long margin. Concentrate. Got a picture in mind?'))

    def test_text_4(self):
        self.assertEqual('" I wrote , \' Making lemonade out of lemons . \' " The post marked the start .',
                         _tokenize('"I wrote, \'Making lemonade out of lemons.\' " The post marked the start.'))

    def test_text_5(self):
        self.assertEqual('" I wrote , " Making lemonade out of lemons . " " The post marked the start .',
                         _tokenize('"I wrote, "Making lemonade out of lemons." " The post marked the start.'))

    def test_text_6(self):
        self.assertEqual("I say , ' Why did I do that ! ' It keeps you inspired !",
                         _tokenize("I say, 'Why did I do that!' It keeps you inspired!"))

    def test_text_7(self):
        self.assertEqual("I say , ' Why did I do that ? ' It keeps you inspired !",
                         _tokenize("I say, 'Why did I do that?' It keeps you inspired!"))

    def test_text_8(self):
        self.assertEqual("They have become my online ' support ' group .",
                         _tokenize("They have become my online 'support' group."))


if __name__ == '__main__':
    unittest.main()
