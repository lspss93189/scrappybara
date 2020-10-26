import unittest

from scrappybara.preprocessing.tokenizer import Tokenizer

_TOKENIZE = Tokenizer()


class TestTokenizer(unittest.TestCase):

    # BLOCKS
    # -------------------------------------------------------------------------->

    def test_indirect_speech_blocks(self):
        self.assertEqual('Well , he said ༺1༻'.split(), _TOKENIZE('Well, he said ༺1༻'))
        self.assertEqual('⦅1⦆ Well , he said ༺1༻'.split(), _TOKENIZE('⦅1⦆ Well, he said ༺1༻'))

    # SHORT TEXT
    # -------------------------------------------------------------------------->

    def test_split_special_words(self):
        self.assertEqual('I can not do that .'.split(), _TOKENIZE('I cannot do that.'))
        self.assertEqual('Can not do that !'.split(), _TOKENIZE('Cannot do that!'))

    def test_links(self):
        self.assertEqual('domain.com'.split(), _TOKENIZE('domain.com'))
        self.assertEqual('Cellucor.com'.split(), _TOKENIZE('Cellucor.com'))
        self.assertEqual('DOMAIN.COM'.split(), _TOKENIZE('DOMAIN.COM'))
        self.assertEqual('sub.domain.com.au'.split(), _TOKENIZE('sub.domain.com.au'))
        self.assertEqual('sub.domain123.com.au'.split(), _TOKENIZE('sub.domain123.com.au'))
        self.assertEqual('data@unicef.org.au'.split(), _TOKENIZE('data@unicef.org.au'))
        self.assertEqual('mr.aid@unicef21.org.au'.split(), _TOKENIZE('mr.aid@unicef21.org.au'))
        self.assertEqual('tacos.pic.twitter.com/Q4usgzGMHq'.split(), _TOKENIZE('tacos.pic.twitter.com/Q4usgzGMHq'))

    def test_dots_single_tokens_nosplit(self):
        self.assertEqual('a.'.split(), _TOKENIZE('a.'))
        self.assertEqual('.end'.split(), _TOKENIZE('.end'))
        self.assertEqual('.End'.split(), _TOKENIZE('.End'))
        self.assertEqual('1 .'.split(), _TOKENIZE('1.'))
        self.assertEqual('.11'.split(), _TOKENIZE('.11'))
        self.assertEqual('1.deliver'.split(), _TOKENIZE('1.deliver'))
        self.assertEqual('1.Deliver'.split(), _TOKENIZE('1.Deliver'))
        self.assertEqual('deliver.1'.split(), _TOKENIZE('deliver.1'))
        self.assertEqual('deliveR.1'.split(), _TOKENIZE('deliveR.1'))
        self.assertEqual('.deliver'.split(), _TOKENIZE('.deliver'))
        self.assertEqual('.Deliver'.split(), _TOKENIZE('.Deliver'))
        self.assertEqual('aaa.deliver'.split(), _TOKENIZE('aaa.deliver'))
        self.assertEqual('aaA.Deliver'.split(), _TOKENIZE('aaA.Deliver'))
        self.assertEqual('$1.3M'.split(), _TOKENIZE('$1.3M'))
        self.assertEqual('1.1'.split(), _TOKENIZE('1.1'))
        self.assertEqual('123.123'.split(), _TOKENIZE('123.123'))
        self.assertEqual('123.123.1'.split(), _TOKENIZE('123.123.1'))
        self.assertEqual('1.1.1.1'.split(), _TOKENIZE('1.1.1.1'))
        self.assertEqual('A.B.1.C'.split(), _TOKENIZE('A.B.1.C'))
        self.assertEqual('A.B.C'.split(), _TOKENIZE('A.B.C'))
        self.assertEqual('A.B.C.'.split(), _TOKENIZE('A.B.C.'))
        self.assertEqual('e.g.'.split(), _TOKENIZE('e.g.'))
        self.assertEqual('e.g'.split(), _TOKENIZE('e.g'))
        self.assertEqual('A.A'.split(), _TOKENIZE('A.A'))
        self.assertEqual('U.S.'.split(), _TOKENIZE('U.S.'))
        self.assertEqual('u.s.'.split(), _TOKENIZE('u.s.'))
        self.assertEqual('1.A'.split(), _TOKENIZE('1.A'))
        self.assertEqual('A.1'.split(), _TOKENIZE('A.1'))
        self.assertEqual('I1.I0I'.split(), _TOKENIZE('I1.I0I'))
        self.assertEqual('items.101'.split(), _TOKENIZE('items.101'))
        self.assertEqual('items.I0I.A'.split(), _TOKENIZE('items.I0I.A'))

    def test_multiple_dots_split(self):
        self.assertEqual('a new ... Sentence'.split(), _TOKENIZE('a new... Sentence'))
        self.assertEqual('bla ...'.split(), _TOKENIZE('bla...'))

    def test_multiple_sentence_enders(self):
        self.assertEqual('a new !!! Sentence'.split(), _TOKENIZE('a new!!! Sentence'))
        self.assertEqual('a new ?? Sentence'.split(), _TOKENIZE('a new?? Sentence'))
        self.assertEqual('a new ??! Sentence'.split(), _TOKENIZE('a new??! Sentence'))

    def test_dots_split(self):
        self.assertEqual('a new . Sentence'.split(), _TOKENIZE('a new.Sentence'))
        self.assertEqual('December 4 . Sentence'.split(), _TOKENIZE('December 4. Sentence'))
        self.assertEqual('try mindfulchef.com . And this .'.split(), _TOKENIZE('try mindfulchef.com. And this.'))
        self.assertEqual('a new . Sentence'.split(), _TOKENIZE('a new. Sentence'))
        self.assertEqual('Fine Arts . She'.split(), _TOKENIZE('Fine Arts. She'))
        self.assertEqual('in june 1962 . Blabla'.split(), _TOKENIZE('in june 1962. Blabla'))
        self.assertEqual('information etc . SVN , NN'.split(), _TOKENIZE('information etc. SVN, NN'))

    def test_dots_nosplit(self):
        self.assertEqual('use .NET'.split(), _TOKENIZE('use .NET'))
        self.assertEqual('a new.sentence'.split(), _TOKENIZE('a new.sentence'))
        self.assertEqual('a new .sentence'.split(), _TOKENIZE('a new .sentence'))
        self.assertEqual('a new. sentence'.split(), _TOKENIZE('a new. sentence'))
        self.assertEqual('market in 2015. includes'.split(), _TOKENIZE('market in 2015. includes'))
        self.assertEqual('the 69th regt. ,'.split(), _TOKENIZE('the 69th regt.,'))
        self.assertEqual('the 69th regt. :'.split(), _TOKENIZE('the 69th regt.:'))
        self.assertEqual('the 69th regt. ;'.split(), _TOKENIZE('the 69th regt.;'))
        self.assertEqual('the 69th regt . )'.split(), _TOKENIZE('the 69th regt.)'))
        self.assertEqual('a srgt . ( born )'.split(), _TOKENIZE('a srgt. (born)'))
        self.assertEqual('4. bought'.split(), _TOKENIZE('4. bought'))
        self.assertEqual('4 . I bought'.split(), _TOKENIZE('4. I bought'))
        self.assertEqual('A. I bought'.split(), _TOKENIZE('A. I bought'))
        self.assertEqual('A. I bought A. I bought'.split(), _TOKENIZE('A. I bought A. I bought'))
        self.assertEqual('1.A. I bought'.split(), _TOKENIZE('1.A. I bought'))
        self.assertEqual('1.A I bought'.split(), _TOKENIZE('1.A I bought'))
        self.assertEqual('( 1 . Todo Cambia )'.split(), _TOKENIZE('(1. Todo Cambia)'))
        self.assertEqual('( 1. todo  )'.split(), _TOKENIZE('(1. todo)'))
        self.assertEqual('manuf. comm. strategies'.split(), _TOKENIZE('manuf. comm. strategies'))
        self.assertEqual('tech ASP .NET'.split(), _TOKENIZE('tech ASP .NET'))
        self.assertEqual('items is N. shore'.split(), _TOKENIZE('items is N. shore'))
        self.assertEqual('his name is A. Gray'.split(), _TOKENIZE('his name is A. Gray'))
        self.assertEqual('his name is a. gray'.split(), _TOKENIZE('his name is a. gray'))
        self.assertEqual('Engage U.S. donors'.split(), _TOKENIZE('Engage U.S. donors'))
        self.assertEqual('the min. is 3'.split(), _TOKENIZE('the min. is 3'))
        self.assertEqual('the Bld. is'.split(), _TOKENIZE('the Bld. is'))
        self.assertEqual('the BLD. is'.split(), _TOKENIZE('the BLD. is'))
        self.assertEqual('he is dr. Robin'.split(), _TOKENIZE('he is dr. Robin'))
        self.assertEqual('Dr. Robin'.split(), _TOKENIZE('Dr. Robin'))
        self.assertEqual('13th ed. New York'.split(), _TOKENIZE('13th ed. New York'))
        self.assertEqual('he is Sr. Programmer'.split(), _TOKENIZE('he is Sr. Programmer'))
        self.assertEqual('bullet 1. do this'.split(), _TOKENIZE('bullet 1. do this'))
        self.assertEqual('bullet 01. do this'.split(), _TOKENIZE('bullet 01. do this'))
        self.assertEqual('bullet.2 do this'.split(), _TOKENIZE('bullet.2 do this'))
        self.assertEqual('of .20 inch'.split(), _TOKENIZE('of .20 inch'))
        self.assertEqual('a. b. ('.split(), _TOKENIZE('a. b. ('))
        self.assertEqual('an n. g. :'.split(), _TOKENIZE('an n. g. :'))
        self.assertEqual('in u.s. !'.split(), _TOKENIZE('in u.s. !'))
        self.assertEqual(', vols. :'.split(), _TOKENIZE(', vols. :'))
        self.assertEqual('a volume . "'.split(), _TOKENIZE('a volume. "'))
        self.assertEqual("a volume . '".split(), _TOKENIZE("a volume. '"))
        self.assertEqual('a volume . ('.split(), _TOKENIZE('a volume. ('))
        self.assertEqual('a volume . )'.split(), _TOKENIZE('a volume. )'))
        self.assertEqual('a volume . ['.split(), _TOKENIZE('a volume. ['))
        self.assertEqual('a volume . ]'.split(), _TOKENIZE('a volume. ]'))
        self.assertEqual('a volume . {'.split(), _TOKENIZE('a volume. {'))
        self.assertEqual('a volume . }'.split(), _TOKENIZE('a volume. }'))
        self.assertEqual('a volume . |'.split(), _TOKENIZE('a volume. |'))
        self.assertEqual('a volume . *'.split(), _TOKENIZE('a volume. *'))

    def test_exclamation_points_split(self):
        self.assertEqual('this is you ! Omg'.split(), _TOKENIZE('this is you! Omg'))
        self.assertEqual('this is you !'.split(), _TOKENIZE('this is you!'))
        self.assertEqual('this is you !!!'.split(), _TOKENIZE('this is you!!!'))
        self.assertEqual('my man ! - marcus'.split(), _TOKENIZE('my man! - marcus'))

    def test_exclamation_points_nosplit(self):
        self.assertEqual('innovate ! project'.split(), _TOKENIZE('innovate! project'))

    def test_non_ambiguous_seperators(self):
        self.assertEqual('this [ is ] you'.split(), _TOKENIZE('this [is] you'))
        self.assertEqual('this ( is ) you'.split(), _TOKENIZE('this (is) you'))
        self.assertEqual('this { is } you'.split(), _TOKENIZE('this {is} you'))
        self.assertEqual('this is you ? omg'.split(), _TOKENIZE('this is you? omg'))
        self.assertEqual('this is you ???'.split(), _TOKENIZE('this is you???'))
        self.assertEqual(r'me \ you'.split(), _TOKENIZE(r'me\you'))
        self.assertEqual('me | you'.split(), _TOKENIZE('me|you'))
        self.assertEqual('the " cat " jumps'.split(), _TOKENIZE('the "cat" jumps'))
        self.assertEqual('the cat ; jumps'.split(), _TOKENIZE('the cat; jumps'))
        self.assertEqual('the cat : jumps'.split(), _TOKENIZE('the cat: jumps'))
        self.assertEqual('failures : include'.split(), _TOKENIZE('failures :include'))
        self.assertEqual('sell > 12'.split(), _TOKENIZE('sell >12'))
        self.assertEqual('sell < 12'.split(), _TOKENIZE('sell <12'))
        self.assertEqual('ca = breakfast'.split(), _TOKENIZE('ca=breakfast'))
        self.assertEqual('targets ='.split(), _TOKENIZE('targets='))

    def test_lt_gt(self):
        self.assertEqual('sell <-- 12'.split(), _TOKENIZE('sell <-- 12'))  # ??
        self.assertEqual('sell -> 12'.split(), _TOKENIZE('sell -> 12'))
        self.assertEqual('This is < me >'.split(), _TOKENIZE('This is <me>'))
        self.assertEqual('Sell > 50%'.split(), _TOKENIZE('Sell >50%'))
        self.assertEqual('Sell < 50%'.split(), _TOKENIZE('Sell <50%'))

    def test_star(self):
        self.assertEqual('discussion * integration'.split(), _TOKENIZE('discussion*integration'))
        self.assertEqual('discussion * integration'.split(), _TOKENIZE('discussion****integration'))
        self.assertEqual('123*123'.split(), _TOKENIZE('123*123'))
        self.assertEqual('123*abc'.split(), _TOKENIZE('123*abc'))

    def test_plus(self):
        self.assertEqual('responsibilities + timeline'.split(), _TOKENIZE('responsibilities+timeline'))
        self.assertEqual('hagen + greg + kris'.split(), _TOKENIZE('hagen+greg+kris'))
        self.assertEqual('LTED + Wifi + BLE + Secret'.split(), _TOKENIZE(' LTED+Wifi+BLE+Secret '))
        self.assertEqual('3+ at'.split(), _TOKENIZE('3+at'))
        self.assertEqual('312+ at'.split(), _TOKENIZE('312+at'))
        self.assertEqual('aa+'.split(), _TOKENIZE('aa+'))

    def test_ampercases(self):
        self.assertEqual('new & old'.split(), _TOKENIZE('new&old'))
        self.assertEqual('New & Old'.split(), _TOKENIZE('New&Old'))
        self.assertEqual('NEW&OLD'.split(), _TOKENIZE('NEW&OLD'))
        self.assertEqual('t&cs'.split(), _TOKENIZE('t&cs'))
        self.assertEqual('T&CS'.split(), _TOKENIZE('T&CS'))
        self.assertEqual('schedule & provide'.split(), _TOKENIZE('schedule& provide'))
        self.assertEqual('schedule & provide'.split(), _TOKENIZE('schedule& provide'))
        self.assertEqual('invest R&D'.split(), _TOKENIZE('invest R&D'))
        self.assertEqual('invest R&D'.split(), _TOKENIZE('invest R &D'))
        self.assertEqual('invest R&D'.split(), _TOKENIZE('invest R& D'))
        self.assertEqual('invest R&D'.split(), _TOKENIZE('invest R & D'))
        self.assertEqual('invest R & 1'.split(), _TOKENIZE('invest R &1'))
        self.assertEqual('invest R & DD'.split(), _TOKENIZE('invest R& DD'))
        self.assertEqual('R&D lab'.split(), _TOKENIZE('R&D lab'))
        self.assertEqual('R&D lab'.split(), _TOKENIZE('R& D lab'))
        self.assertEqual('R&D lab'.split(), _TOKENIZE('R &D lab'))
        self.assertEqual('R&D lab'.split(), _TOKENIZE('R & D lab'))
        self.assertEqual('invest R&D lab'.split(), _TOKENIZE('invest R&D lab'))
        self.assertEqual('invest R&D lab'.split(), _TOKENIZE('invest R &D lab'))
        self.assertEqual('invest R&D lab'.split(), _TOKENIZE('invest R& D lab'))
        self.assertEqual('invest R&D lab'.split(), _TOKENIZE('invest R & D lab'))
        self.assertEqual('invest AR&D lab'.split(), _TOKENIZE('invest A R & D lab'))
        self.assertEqual('invest R&DA lab'.split(), _TOKENIZE('invest R & D A lab'))
        self.assertEqual('invest RR & R2 A lab'.split(), _TOKENIZE('invest RR & R2 A lab'))
        self.assertEqual('kitchen & utility'.split(), _TOKENIZE('kitchen&utility'))

    def test_slashes(self):
        self.assertEqual('10/10/2010'.split(), _TOKENIZE('10/10/2010'))
        self.assertEqual('b2b / b2c'.split(), _TOKENIZE('b2b/b2c'))
        self.assertEqual('me / you'.split(), _TOKENIZE('me/you'))
        self.assertEqual('me / you'.split(), _TOKENIZE('me /you'))
        self.assertEqual('me / you'.split(), _TOKENIZE('me/ you'))
        self.assertEqual('/ external'.split(), _TOKENIZE('/external'))
        self.assertEqual('p/a'.split(), _TOKENIZE('p/a'))
        self.assertEqual('A/B'.split(), _TOKENIZE('A/B'))
        self.assertEqual('A/'.split(), _TOKENIZE('A/'))
        self.assertEqual('/B'.split(), _TOKENIZE('/B'))

    def test_dashes(self):
        self.assertEqual('Mon-Khmer'.split(), _TOKENIZE('Mon–Khmer'))
        self.assertEqual('— this'.split(), _TOKENIZE('—this'))

    def test_percentage(self):
        self.assertEqual('%12'.split(), _TOKENIZE('%12'))
        self.assertEqual('12%'.split(), _TOKENIZE('12%'))
        self.assertEqual('% savings'.split(), _TOKENIZE('%savings'))
        self.assertEqual('save % savings'.split(), _TOKENIZE('save%savings'))

    def test_colon(self):
        self.assertEqual('example : bla'.split(), _TOKENIZE('example: bla'))
        self.assertEqual('raise Q1 : Raise 1$'.split(), _TOKENIZE('raise Q1: Raise 1$'))
        self.assertEqual('support : revise'.split(), _TOKENIZE('support:revise'))
        self.assertEqual('payroll : hr'.split(), _TOKENIZE('payroll:hr'))
        self.assertEqual('Support : Revise'.split(), _TOKENIZE('Support:Revise'))
        self.assertEqual('re:invent'.split(), _TOKENIZE('re:invent'))
        self.assertEqual('conduct 1:1s'.split(), _TOKENIZE('conduct 1:1s'))
        self.assertEqual('ISO 123:123'.split(), _TOKENIZE('ISO 123:123'))
        self.assertEqual('A:B'.split(), _TOKENIZE('A:B'))
        self.assertEqual('step : 703'.split(), _TOKENIZE('step:703'))
        self.assertEqual('Sell 12 :'.split(), _TOKENIZE('Sell 12:'))
        self.assertEqual('Strategy : HR'.split(), _TOKENIZE('Strategy:HR'))
        self.assertEqual('2 : HR'.split(), _TOKENIZE('2:HR'))
        self.assertEqual('12243 : engage'.split(), _TOKENIZE('12243:engage'))

    def test_arrows(self):
        self.assertEqual('Sell 12->23'.split(), _TOKENIZE('Sell 12->23'))
        self.assertEqual('Sell 12 > 23'.split(), _TOKENIZE('Sell 12>23'))
        self.assertEqual('a => b'.split(), _TOKENIZE('a = > b'))
        self.assertEqual('x >= 12.5'.split(), _TOKENIZE(' x > = 12.5'))
        self.assertEqual('x <= 12.5'.split(), _TOKENIZE(' x < = 12.5'))

    def test_comas(self):
        self.assertEqual('hello , hi'.split(), _TOKENIZE('hello, hi'))
        self.assertEqual('123 , all good'.split(), _TOKENIZE('123, all good'))
        self.assertEqual('all good , 123'.split(), _TOKENIZE('all good,123'))
        self.assertEqual('123,123'.split(), _TOKENIZE('123,123'))

    def test_single_quotes(self):
        self.assertEqual("Rocco 's blob".split(), _TOKENIZE("Rocco 's blob"))
        self.assertEqual("His name is ' Rob ' bob".split(), _TOKENIZE("His name is 'Rob' bob"))
        self.assertEqual("His name is Rob ' bob '".split(), _TOKENIZE("His name is Rob 'bob'"))
        self.assertEqual("launch ' go live ' strategy".split(), _TOKENIZE("launch 'go live'strategy"))
        self.assertEqual("james o'hare".split(), _TOKENIZE("james o'hare"))
        self.assertEqual("' proposal".split(), _TOKENIZE("'proposal"))
        self.assertEqual('Deliver 4ft'.split(), _TOKENIZE("Deliver 4'"))
        self.assertEqual('Deliver 4in'.split(), _TOKENIZE('Deliver 4"'))
        self.assertEqual('Deliver 4ft4in'.split(), _TOKENIZE('Deliver 4\'4"'))
        self.assertEqual("' we will run items again '".split(), _TOKENIZE("'we will run items again'"))
        self.assertEqual("ceo order ' macbook pro '".split(), _TOKENIZE("ceo order 'macbook pro'"))
        self.assertEqual("rock 'n' roll".split(), _TOKENIZE("rock 'n' roll"))
        self.assertEqual("rock 'n roll".split(), _TOKENIZE("rock 'n roll"))
        self.assertEqual("rock n' roll".split(), _TOKENIZE("rock n' roll"))

    def test_clitics(self):
        self.assertEqual("Jane 's blob".split(), _TOKENIZE("Jane's blob"))
        self.assertEqual("sdo 's".split(), _TOKENIZE("sdo's"))
        self.assertEqual("make SOP 's today".split(), _TOKENIZE("make SOP's today"))
        self.assertEqual("I 'd eat".split(), _TOKENIZE("I'd eat"))
        self.assertEqual("I 'm blob".split(), _TOKENIZE("I'm blob"))
        self.assertEqual("They 'll come".split(), _TOKENIZE("They'll come"))
        self.assertEqual("They 're blobs".split(), _TOKENIZE("They're blobs"))
        self.assertEqual("They 've eaten".split(), _TOKENIZE("They've eaten"))
        self.assertEqual("They are n't blobs".split(), _TOKENIZE("They aren't blobs"))
        self.assertEqual("They ca n't blobs".split(), _TOKENIZE("They can't blobs"))
        self.assertEqual("They have n't blobs".split(), _TOKENIZE("They haven't blobs"))
        self.assertEqual("They is n't blobs".split(), _TOKENIZE("They isn't blobs"))
        self.assertEqual('ifp \'s'.split(), _TOKENIZE('ifp\'s'))

    def test_multi_special_chars(self):
        self.assertEqual('bla // bla'.split(), _TOKENIZE('bla // bla'))
        self.assertEqual('bla {{ bla }}'.split(), _TOKENIZE('bla {{bla}}'))
        self.assertEqual('bla {{ bla }}'.split(), _TOKENIZE('bla {{bla}}'))

    def test_bullets(self):
        self.assertEqual('year . * introduce'.split(), _TOKENIZE('year. *introduce'))
        self.assertEqual('year . - introduce'.split(), _TOKENIZE('year. -introduce'))

    def test_special_chars(self):
        self.assertEqual('_tag #MenArePigs'.split(), _TOKENIZE('_tag #MenArePigs'))
        self.assertEqual('_tag @MenArePigs'.split(), _TOKENIZE('_tag @MenArePigs'))

    def test_protected_patterns(self):
        self.assertEqual('visit http://bla.com.au'.split(), _TOKENIZE('visit http://bla.com.au'))
        self.assertEqual('visit https://bla.com.au/'.split(), _TOKENIZE('visit https://bla.com.au/'))
        self.assertEqual('visit www.bla.com.au/bla.pdf'.split(), _TOKENIZE('visit www.bla.com.au/bla.pdf'))
        self.assertEqual('visit www.Bla.com and www.Bla2.com'.split(), _TOKENIZE('visit www.Bla.com and www.Bla2.com'))

    def test_sentence_parts(self):
        self.assertEqual('on Oct. 29 , 2017 .'.split(), _TOKENIZE('on Oct. 29, 2017.'))
        self.assertEqual('involve the U.S. ?'.split(), _TOKENIZE('involve the U.S.?'))
        self.assertEqual('" Jump " , he said .'.split(), _TOKENIZE('"Jump", he said.'))
        self.assertEqual('" Jump . " , he said .'.split(), _TOKENIZE('"Jump.", he said.'))
        self.assertEqual('" Jump . " he said .'.split(), _TOKENIZE('"Jump." he said.'))

    def test_multi_dots(self):
        self.assertEqual('Ms. Dean .'.split(), _TOKENIZE('Ms. Dean.'))
        self.assertEqual('Ms. Dean . Mrs Dean .'.split(), _TOKENIZE('Ms. Dean. Mrs Dean.'))
        self.assertEqual('Sgt. Pepp. went there'.split(), _TOKENIZE('Sgt. Pepp. went there'))

    def test_smileys(self):
        self.assertEqual(':-)'.split(), _TOKENIZE(':-)'))

    # LONG TEXT
    # -------------------------------------------------------------------------->

    def test_text_1(self):
        self.assertEqual('said Lt. Gov. Brian Calley in a Dec. 19 press release .'.split(),
                         _TOKENIZE('said Lt. Gov. Brian Calley in a Dec. 19 press release.'))

    def test_text_2(self):
        self.assertEqual('headquarters in Ghent , Belgium . The company develops'.split(),
                         _TOKENIZE('headquarters in Ghent, Belgium. The company develops'))

    def test_text_3(self):
        self.assertEqual('The fastest in the world , by a long margin . Concentrate . Got a picture in mind ?'.split(),
                         _TOKENIZE('The fastest in the world, by a long margin. Concentrate. Got a picture in mind?'))

    def test_text_4(self):
        self.assertEqual('" I wrote , \' Making lemonade out of lemons . \' " The post marked the start .'.split(),
                         _TOKENIZE('"I wrote, \'Making lemonade out of lemons.\' " The post marked the start.'))

    def test_text_5(self):
        self.assertEqual('" I wrote , " Making lemonade out of lemons . " " The post marked the start .'.split(),
                         _TOKENIZE('"I wrote, "Making lemonade out of lemons." " The post marked the start.'))

    def test_text_6(self):
        self.assertEqual("I say , ' Why did I do that ! ' It keeps you inspired !".split(),
                         _TOKENIZE("I say, 'Why did I do that!' It keeps you inspired!"))

    def test_text_7(self):
        self.assertEqual("I say , ' Why did I do that ? ' It keeps you inspired !".split(),
                         _TOKENIZE("I say, 'Why did I do that?' It keeps you inspired!"))

    def test_text_8(self):
        self.assertEqual("They have become my online ' support ' group .".split(),
                         _TOKENIZE("They have become my online 'support' group."))


if __name__ == '__main__':
    unittest.main()
