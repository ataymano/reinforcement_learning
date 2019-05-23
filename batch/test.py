from common import vw

trainer = vw.Vw(path='/Users/ataymano/tmp/vw',
                opts="--dsjson --cb_adf",
                tmp_folder='/Users/ataymano/tmp/tmp1')

print(trainer.get_model())
trainer.train('/Users/ataymano/tmp/dsjson/30_0.json')
print(trainer.get_model())
trainer.train('/Users/ataymano/tmp/dsjson/03_0.json')
print(trainer.get_model())

