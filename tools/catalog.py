"""Source of truth for the catalog. Edit the add(...) lines, then run:  python3 tools/catalog.py
It rewrites the CATALOG block inside index.html. Quality (q) is a per-channel estimate plus a small bonus."""
import json,re
SSS='Super Simple Songs'; CC='ChuChu TV Hindi'; IB='Infobells Hindi'; SE='Sesame Street India'; VN='Vlad and Niki Hindi'
Q={SSS:88,CC:80,IB:78,SE:85,VN:60}
rows=[]
def add(cat,sub,lang,ch,items,energy='medium',level=1,bonus=0):
    for it in items:
        vid,secs,title=it[0],it[1],it[2]
        e=it[3] if len(it)>3 else energy
        lv=it[4] if len(it)>4 else level
        rows.append(dict(id=vid,cat=cat,sub=sub,lang=lang,level=lv,secs=secs,energy=e,q=Q[ch]+bonus,ch=ch,t=title))

# 1 Words and naming
add(1,'colours','hi',CC,[('Z_qvUJo3DiM',188,'Laal Hara Peela colours song'),('X0M_e9Zblk8',291,'I See Colours (Hindi)'),('CxNSqSKwK_o',243,'Rainbow party colours song (Hindi)')])
add(1,'colours','hi',IB,[('Ndk11X336z8',176,'Laal Laal Laal rang geet'),('53Wj3VfkpxA',97,'Meri Topi Ka Rang Hai Peela')])
add(1,'colours','en',SSS,[('wceMsYSyNUQ',160,'The Rainbow Song'),('aMTIm-D1l54',120,'Red Yellow Green Blue'),('jYAWf8Y91hA',183,'I See Something Blue'),('Asb8N0nz9OI',184,'I See Something Pink'),('zxIpA5nF_LY',122,'What Is Your Favorite Color?')],bonus=2)
add(1,'animals','hi',IB,[('0qO7uFmrz5Y',175,'Gaiya Meri: farm animal sounds'),('S_fU1ys2iBg',112,'Jungle Jungle animal song')])
add(1,'animals','hi',CC,[('FG9G0tw9peM',519,'Jungle song with wild animal names'),('g9uHieWeWQE',230,'Zoo Friends song (Hindi)'),('ysF3xbRknaQ',217,'Wheels on the Bus: farm animals (Hindi)')])
add(1,'animals','en',SSS,[('zXEq-QO3xTg',204,'The Animals On The Farm'),('OwRmivbNgQk',240,'Let Us Go To The Zoo','lively'),('5oYKonYBujg',210,'Old MacDonald Had A Farm'),('uZrFDgO0sMQ',151,'If I Were a Duck: animal sounds'),('pWepfJ-8XU0',145,'I Have A Pet'),('GoSq-yZcJ-4',205,'Walking In The Jungle','lively')],bonus=2)
add(1,'food','hi',CC,[('p8omFrIPdVQ',402,'Yes Yes Fruits song (Hindi)'),('cmcUUwfTSx0',302,'Fruit Friends song (Hindi)')])
add(1,'food','en',SSS,[('frN3nvhIHUk',163,'Do You Like Broccoli Ice Cream?')],bonus=3)
add(1,'body','hi',CC,[('9MZM5F-uFwg',186,'Five Senses song (Hindi)')])
add(1,'body','en',SSS,[('eBVqcTEC3zQ',145,'One Little Finger'),('WX8HmogNyCY',114,'Head Shoulders Knees and Toes','lively')],bonus=2)
add(1,'vehicles','hi',IB,[('kzQSmh-QUhg',148,'School Bus Aayi Pom Pom Pom')])
add(1,'vehicles','hi',CC,[('jIc0tDqZpX4',142,'Wheels on the Bus (Hindi)')])
add(1,'vehicles','hi',SE,[('XYtL9kRr7Lg',136,'The Wheels on the Fire Truck (Hindi)')])
add(1,'family','hi',IB,[('_HC3v4dMafU',98,'Mere Ghar Me Milta Hai Pyaar'),('oXsmQy3hMXs',164,'Mummy Mummy Mere Paas Aao'),('xn09YpHzhQM',187,'Papa Papa father song')])
add(1,'family','hi',CC,[('61bG1hs6Duc',358,'Finger Family song (Hindi)')])

# 2 Rhymes and songs
add(2,'rhymes','hi',CC,[('_BltB-q3zNA',161,'Machli Jal Ki Rani Hai'),('CxNQ8w_5Vg8',167,'Baa Baa Black Sheep (Hindi)'),('yJkIJ5OcAdA',151,'Incy Wincy Spider (Hindi)'),('bRX_k2uElZI',152,'Humpty Dumpty (Hindi)'),('hOfUswapTJ8',170,'Hickory Dickory Dock (Hindi)'),('E53vZJQhJjI',181,'Rain Rain Go Away (Hindi)')])
add(2,'rhymes','hi',IB,[('GsIyqH8oDao',179,'Bandar Mama Pahan Pajama'),('71Xe1JqnGAE',182,'Aloo Kachaloo Beta Kahan Gaye The'),('MHjaCfDh_Mk',153,'Kalu Madari Aaya')])
add(2,'rhymes','en',SSS,[('9mmF8zOlh_g',166,'BINGO'),('bne3Ix_tJL8',144,'The Eensy Weensy Spider'),('YE7PiTwhTQk',177,'Mary Had A Little Lamb'),('HGgsklW-mtg',182,'Hickory Dickory Dock'),('hlzvrEfyL2Y',151,'Mr. Golden Sun'),('GR2o6k8aPlI',190,'Baby Shark'),('LFrKYjrIDs8',156,'Rain Rain Go Away')])
add(2,'action','en',SSS,[('VsgpUHUYuJI',203,'Move! dance song'),('hW2DDGX7Tcc',107,'Follow Me'),('fN1Cyr0ZK9M',92,'Hello Hello! Can You Clap Your Hands?'),('fPMjnlTEZwU',112,'Walking Walking'),('l4WNrvVjiTw',124,'If You Are Happy'),('3zm5JMGIsRU',179,'Baby Elephant: get up and move'),('GukdT4gUlZs',180,'Wag Your Tail')],energy='lively',bonus=3)
add(2,'action','hi',SE,[('h7nxDVK8nhk',187,'If You Are Happy and You Know It (Hindi)'),('ivZ2MOT0Z5o',126,'Cookie Shark (Hindi)')],energy='lively')
add(2,'action','hi',CC,[('hWp-CruPRUw',192,'Baby Shark (Hindi)')],energy='lively')
add(2,'calm','en',SSS,[('yCjJyiqpAuU',154,'Twinkle Twinkle Little Star'),('OKbpLQp509Y',188,'Sweet Dreams goodnight song'),('7otAJa3jui8',122,'Row Row Row Your Boat'),('tbbKjDjMDok',169,'Little Snowflake'),('ug1pI-Ephns',148,'Skidamarink')],energy='calm')
add(2,'calm','hi',CC,[('6NSE_7rP2Wg',224,'Jagmag Jagmag Chhote Taare (stargazing)'),('xlxIgkeUzfg',309,'Twinkle Twinkle Little Star (Hindi)'),('Km3tqza7C8E',404,'Lori geet: bedtime song (Hindi)')],energy='calm')

# 3 Early concepts
add(3,'counting','hi',CC,[('GwYXMliCKvY',245,'Ten in the Bed (Hindi number rhyme)'),('V7McjY3FOLI',234,'Five Little Monkeys (Hindi)')])
add(3,'counting','hi',SE,[('q8EmMmetonQ',155,'Five Little Ducks (Hindi)')])
add(3,'counting','en',SSS,[('pTLtcno5_cY',119,'Seven Steps'),('xNw1SSz18Gg',182,'How Many Fingers?'),('pZw9veQ76fo',174,'Five Little Ducks'),('VNRNAloCb5Y',127,'10 Little Airplanes'),('Aq4UAss33qA',92,'Count And Move','lively'),('zQ5bQ6tjl_M',217,'Stomp! Count to five','lively'),('Vr-L6q4vbWU',96,'The Bananas Song'),('ZhODBFQ2-bQ',130,'Five Little Monkeys')],bonus=2)
add(3,'shapes','en',SSS,[('TJhfl5vdxp4',251,'The Shape Song 1'),('03pyY9C2Pm8',251,'The Shape Song 2','medium',2),('hDqWTltrGJ8',175,'Shapes I See At The Beach')],bonus=2)
add(3,'letters','hi',CC,[('TM83zp1AkUM',190,'A Se Anar: Hindi varnamala geet'),('Jp5QHUOl13g',242,'A Se Amrud: Hindi varnamala geet'),('h4hJyaMhjdg',251,'Ka Se Kamal: Hindi varnamala geet 2','medium',2)])
add(3,'letters','en',SSS,[('vD98OvvDNEs',185,'The Alphabet Song'),('kDdg2M1_EuE',125,'The Alphabet Is So Much Fun')])
add(3,'opposites','en',SSS,[('RNUZBHlRH4Y',148,'Open Shut Them: opposites')],bonus=3)

# 4 Stories (story-songs for now)
add(4,'stories','hi',CC,[('3DbOz9XF6nc',381,'First Day of School (Hindi)'),('J8C_5MneGwg',267,'Picnic at Home (Hindi)'),('DBk7s6tz3Zg',395,'Yatra Ka Gaana: travelling song'),('9CtuEOPE-aE',280,'Baby Goes Fishing (Hindi)'),('P3LpU0Meb9k',270,'Baby goes to Old MacDonald farm (Hindi)'),('eE_kuS294HU',348,'Circus song (Hindi)')],level=2)

# 5 Thinking and problem solving
add(5,'thinking','en',SSS,[('EULQrI3aVik',94,'Mystery Box 1: what is inside?'),('4pfuapihZhI',94,'Mystery Box 2: what is inside?'),('Bd1yjm_zopI',94,'Mystery Box 3: what is inside?'),('Tt_S9qoupAk',194,'Hide And Seek'),('OzKY5YHnOTg',123,'Who Took The Cookie?'),('YVgv1EFJZHc',193,'What Do You Hear? guess the animal'),('PmpJzVCIisc',181,'There Is An Animal That I See'),('ddDN30evKPc',152,'Do You Like Spaghetti Yogurt?')],bonus=4)
add(5,'thinking','hi',SE,[('gCaiWovBbQs',110,'Peek-A-Boo with Elmo (Hindi)')],bonus=3)
add(5,'thinking','hi',IB,[('i3WrZ2GdLxc',159,'Dada-Dadi Ka Ghar: hide and seek')],bonus=3)

# 6 Create and do
add(6,'create','en',SSS,[('AlB6ZNqykXU',151,'I Like To Draw: colours and shapes'),('3noL0nBOD4M',110,'Rock Scissors Paper 2: finger play'),('lvI12tC7zro',114,'Rock Scissors Paper 3: finger play'),('JRMAptlBgTk',130,'We All Fall Down: walk around the circle','lively'),('JV-D_K4drsA',205,'The Pinocchio dance','lively')],bonus=2)
add(6,'create','hi',CC,[('CahSfDVu5zs',219,'Cake Banao: pat a cake (Hindi)')])

# 7 Real world
add(7,'world','en',SSS,[('rD6FRDd9Hew',127,'How Is The Weather?'),('7SxqpsDI2ho',171,'Little Birdie','calm'),('EO1GV4qUxgE',153,'8 Little Planets','medium',2)])
add(7,'world','hi',CC,[('prZkKDj_qj4',163,'Bahar Khelo: play outside (Hindi)'),('5MjPmBtenvY',146,'The Beach song (Hindi)'),('DDszwyYq7tQ',274,'Baby Goes Swimming (Hindi)')])
add(7,'world','hi',IB,[('GjUxiTEcWTw',87,'I Love India')])

# 8 Daily life and feelings
add(8,'routines','hi',IB,[('fQENf-0K60I',80,'Brush Karo Brush Karo'),('0zLWoXoMD20',182,'Time to bath: clean up song (Hindi)'),('D8Wmi1EA7vg',119,'Lalaji bathtime: save water')])
add(8,'routines','hi',CC,[('jLvxa0k-n7g',181,'Bath song: Chalo Nahayein'),('HIPMdP1g0BY',234,'Brush my teeth song (Hindi)')])
add(8,'routines','en',SSS,[('wCio_xVlgQ0',135,'Brush Your Teeth'),('4XLQpRI_wOQ',139,'This Is The Way'),('HVYXHMY7wvo',137,'The Bath Song'),('SFE0mMWbA-Y',110,'Clean Up Song'),('-jBfb33_KHU',182,'Put On Your Shoes'),('PraN5ZoSjiY',121,'Bye Bye Goodbye','calm')],bonus=2)
add(8,'feelings','hi',CC,[('f-8CiTDW6lM',226,'Care and Share song (Hindi)'),('4-2Yi5QHK9E',227,'Helping Mommy song (Hindi)'),('OIlgG6wKHGg',245,'Hello song (Hindi)'),('4dCIPVXSKtw',306,'Stay Safe song (Hindi)')])
add(8,'feelings','en',SSS,[('VvJJeqVo3vk',103,'I Like You','calm')],bonus=2)

# 9 Treat shelf
add(9,'treat','hi',VN,[('nLOZFYTAMuM',481,'Vlad and Niki: shapes at the giant house'),('nQA3YP1Qgjo',561,'Vlad and Niki: toy monster truck ride'),('cWBRtXrmJeE',485,'Vlad and Niki: four colours playhouse'),('PVbZJOeszhc',320,'Vlad and Niki: travel stories'),('nqycusOAVMA',536,'Vlad and Niki: fun and useful stories')],energy='lively')

ids=[r['id'] for r in rows]
assert len(ids)==len(set(ids)),[i for i in ids if ids.count(i)>1]
assert all(re.fullmatch(r'[A-Za-z0-9_-]{11}',i) for i in ids)
from collections import Counter
print('total',len(rows),'by cat',sorted(Counter(r['cat'] for r in rows).items()),'lang',Counter(r['lang'] for r in rows),'calm',sum(r['energy']=='calm' for r in rows))
js=json.dumps(rows,ensure_ascii=True,separators=(',',':')).replace('},{','},\n    {')
import os
p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html')
s=open(p,encoding='utf-8').read()
s2=re.sub(r'/\*CATALOG_START\*/.*?/\*CATALOG_END\*/',lambda m:'/*CATALOG_START*/'+js+'/*CATALOG_END*/',s,flags=re.S)
assert '/*CATALOG_START*/' in s, 'CATALOG markers missing from index.html'
open(p,'w',encoding='utf-8').write(s2)
print('catalog written into index.html')
