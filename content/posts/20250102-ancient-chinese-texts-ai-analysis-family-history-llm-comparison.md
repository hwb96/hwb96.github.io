+++
title = "古籍、AI 与我的家族历史：兼论中外大模型在古文识别中的表现"
date = 2025-01-02T23:52:40+08:00
images = []
tags = []
categories = []
draft = false
+++
几年前，我得到了一份珍贵的古籍家谱，在我手里待了 30 分钟，这是一本写着我从哪里来的古籍。 高中三年真正培养了我阅读古文的能力，而这种能力将使我受益终身。
趁着我的古文阅读水平还在，我决定借助大模型的力量，将他们翻译出来。

我发现大模型的能力真的参差不齐，美国的大模型识别中文古文的能力让我大吃一惊，比国内任意一家的能力都要好。
我会在文末放出各自的翻译截图，我分别测试了8家大模型，分别是： 国外的：Gemini，Claude，OpenAI ，国内的：通义千问，kimi，deepseek，智谱AI，豆包。

我心目中的对于古籍识别排序的能力排名是这样的：

Gemini > >  通义千问 >  Claude-3.5-Sonnet= gpt-4o= kimi > deepseek v3 = GLM > > 豆包

Gemini 最好，通义千问是接下来的佼佼者。 其他Claude-3.5-Sonnet，gpt-4o，kimi，deepseek v3都是基本还能看下去，但是deepseek v3不懂得古文是从右到左的。 GLM识别重复特别多，但是能识别出里边的内容，豆包就好像是完全在想象。

识别出的内容我放在了附录里。
<!--more-->
--- 
我看着这些古文字，一页一页翻着，看着黑色的墨迹方方正正。我想象着家人以前的样子，以及我脑海中幻想他们穿着长袍长途跋涉从山西下山的样子。他们就在这里呆了几十代人，我想象着他们一代一代的人生将会如何：十七八岁时，甚至更早，她们会结婚。长大后将分给农地的一个角落，他们会在那里盖间房子，下一代也是如此。我也本将如此。

我想起了塔拉·韦斯特弗书里的话，“在过去的十年里，我穿越的距离——物理上的和精神上的——几乎让我无法呼吸，让我思考起自己是否已改变得太多。我所有的学习、阅读、思考和旅行，是否已将我变成一个不再属于任何地方的人？我想起那个女孩，那个除了她的废料场和大山，一无所知的女孩。”我和她一样。直到我这一代才走出大山，走出他们生活了几十代的地方，从山西走之后，几百年间，他们从未离开过这里。

我当时用手机拍了照片之后就匆匆还了回去。后来，我的苹果手机换了之后，我以为我保存在了我的百度网盘里，但是我怎么也找不到了。今天我突然登上我的iCloud，发现几张尘封已久的照片截图，我真的非常感慨，这就是我失去的珍贵之物。

## 家谱的前两页

![image-20250102215212354](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102215212354.png)

![image-20250102215224414](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102215224414.png)

## 内容提取

手工校对后的内容及其翻译：

### 序章

```text
賜姓，胙土，命氏，子孫世守其家數千年不忘其所自始太史公之著史記也

公侯傳國 名曰世家 亦其遺意也 魏晉以降九品之中正之法行

往往競以門第相高 如王谢，崔虞之类，未免依托矫枉，浸失古意，贵族先世理學儒宗，王侯將相，代不乏人，譜之發凡起例，必有可以為世法者，余未識原本，且拙於文，奚足增光貴族，族長曰，吾先世晋人也，元季劉福通诸寇， 蹂躏中原，河南淮北數千里，人烟一空。

明太祖定鼎後，查都省戶口繁殷之區，下詔遷之，俾入地適均，故吾族肇遷始祖諱溫者，於永樂年間由晋省洪洞縣來密县，占籍平陌镇，先世之在晋者失考， 今居密者，虽有 曠代兵荒之隔，然前世谱牒踵修，以信传信，以疑传疑，名下各有小注，暨序文可徵，无烦先生椽笔，且吾 谱之修，宜质不宜文，一切依附矫诬之辞，均不敢出， 惟是一本之亲，昭穆之序，支分派别，瞭然可溯于册， 俾吾族之众，咸知敦睦族之风，而後子孙踵继而修明之，有所籍以式，替吾等之願畢，矣余善其言，深 得古人之意而諾之，蓋韓族與吾族，世世姻聯，尤為 久交，不得以虛飾應，因忘己之固陋，援筆著其本始， 並推其意，有合於古者，以告後之人，傳後之子孫，觀 斯譜也，尚思繩其祖武，以無負族長修譜之志則孝矣。

本族中輩數字

十七世十八世十九世二十世二十一世二十二世二十三世

普 朝 欽 汝 格 熙 增

日陽 月陰 金生水生木生火生土

邑庠生 王致福 頓首拜序

始祖温，字师孔，号平野，原籍山西洪洞人。明初奉旨迁密，兄弟三人：长温、次和、三节。相传播迁时，家有铁斧，分而为三，各持其一以为识。次迁鄢陵，三迁温县，今皆为望族，各有谱牒。长迁于平陌村，遂家马是为在密县之始祖懿行難以枚举殁葬于村之西北原配盧氏生三子。

长仲兴，次仲良，三仲诚。
```



### 现代译文

赐姓、封地、命名氏族，这些都是古代的传统，子孙后代世世代代守护着家族的根基，不忘其起源，就像太史公司马迁在《史记》中所记载的一样。

公侯们传承国家，他们的故事被称作“世家”，这也是古代传统的一部分。从魏晋时期开始，社会上流行根据门第来评价人的高低，比如王家和谢家、崔家和虞家等大族，都以出身高贵而自傲。

但这样的风气逐渐失去了古时的真实意义。贵族家庭里有理学大师、儒家学者、王侯将相，每一代都不缺乏人才。编写族谱时，应该遵循一定的规则，为后人提供典范。

我并未见过你们的原始资料，并且我的文笔也不够好，不足以给贵家族增光添彩。不过，族长告诉我，家族最早是来自晋地（山西）的人，在元末刘福通等人入侵中原地区的时候，河南淮北一带遭受了严重的破坏，人口稀少。

明朝建立后，为了平衡各地的人口分布，明太祖下令迁移人口。因此，我们这一支由始祖温先生带领，在永乐年间从山西洪洞县搬迁到了密县平陌镇定居下来。

关于在晋期间的先辈事迹已经难以考证，但现今居住在密县的家族成员，尽管经历了战争和饥荒，仍然保持着对前辈族谱的修订。这些记录真实可信，对于不确定的事情也如实记录，每个名字下都有小注解，以及序言可以作为证据，不需要我多加修饰。

族谱应注重平实而非华丽的文字，避免一切不实或夸大的言辞，家谱的目的是让家族成员清楚自己的血缘关系，确保世系清晰可追溯。这样，家族的所有成员都能明白团结和睦的重要性，并且后代会继续修缮和完善这份族谱，以此来纪念和延续族长修谱的心愿。

我非常赞同他的观点，认为这与古人编修族谱的初衷相符，所以答应了他的请求。因为韩家与我家世代联姻，交往甚久，不能虚情假意应对，所以我决定尽力帮助他完成这个重要的任务，希望后代子孙能够铭记祖先的事迹，不负族长修谱的心意，这才是真正的孝道。

书写人：邑庠生王致福

敬拜并撰写此序。

------

本族中輩數字

十七世：普
十八世：朝
十九世：钦
二十世：汝
二十一世：格
二十二世：熙
二十三世：增

日陽 月陰 金生水生木生火生土

------

始祖温，字师孔，号平野，原本是山西洪洞人。明朝初年遵照皇上的旨意迁移到密县，当时兄弟三人一起搬家，他们分别是老大温、老二和、老三节。据说搬家时，家里有一把铁斧头，他们把它分成三份，每人拿一份作为标识。后来，老二搬到了鄢陵，老三去了温县，现在都是有名望的家庭，各自有自己的族谱。而老大则来到平陌村安家，这就是我们在密县的始祖。始祖的行为准则难以一一列举，他去世后葬在村子西北边。他的妻子卢氏给他生了三个儿子，分别是仲兴、仲良和仲诚。

## 附录

### Gemini

![image-20250102221200529](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102221200529.png)

![image-20250102221526187](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102221526187.png)

它还能解释里边的古文给你，特别是里边的专有名词，我觉得其他模型在这方面和他差一大截：

```text
Certainly! Here's a breakdown of the text, including a translation and some commentary:

Original Text with Punctuation (Based on standard Chinese style):

賜姓胙土，命氏子孫世守其家數千年不忘其所，始太史公之著史記也。公侯傳國，名曰世家，亦其遺意也。魏晋以降，九品中正之法行，往往競以門第相高，如王謝崔虞之類，未免依托矯誣，浸失古意貴族。先世理學儒宗，王侯將相代不乏人，譜之發凡起例，必有可以為世法者，余未識原本，且拙於文，奚足增光。貴族族長曰，吾先世晋人也。元季劉福通諸冠，躪中原，河南淮北數千里，人烟一空。明太祖定鼎後，查都省戶口繁殷之區，下詔遷之，俾人地適均。故吾族肇遷，始祖諱溫者於永樂年間由晋省洪洞縣來，密占籍平陌鎮。先世之在晋者失孜，今居密者雖有壙代兵荒之隔，然前世譜牒踵修，以信傳信，以疑傳疑，名下各有小註暨序文可徵，無煩先生檬筆。且吾諧之修，宜質不宜文，一切依附矯誣之辭，均不敢出。惟是一本之親朋穆之序支分派別，瞭然可溯於冊。俾吾族之泉咸和敦親睦族之風，而後子孫踵繩而

Translation:

"The granting of a surname and land, with the descendants being charged to guard their home for thousands of years, not forgetting their origins, was first recorded by the Grand Historian (Sima Qian) in the Records of the Grand Historian. The feudal lords transmitting their states, called "hereditary houses" is also a testament to this idea. After the Wei and Jin dynasties, the Nine Rank System for Officials was implemented, often leading to the competition of families for status, such as the Wang, Xie, Cui, and Yu families. This was ultimately unavoidable because of reliance on falsification, gradually losing the original idea of nobility. Our ancestors, versed in Confucianism and scholars, and those who were ministers and nobles were numerous. There are countless records and rules of genealogy being started. Surely, this could become law for the world, but I have not seen the original, and since my writing is poor, how can I add to its brilliance?

The clan chief of our noble family said, "Our ancestors were people of Jin. During the Yuan dynasty, the rebels of Liu Futong devastated the Central Plains. Thousands of miles of land in the south of the Yellow River and north of the Huai River were rendered desolate. After the founding of the Ming dynasty by Grand Ancestor, he investigated the heavily populated areas in all the provinces and issued an imperial decree to move people, so that the land could be redistributed fairly. Therefore, our clan was moved and our ancestor, whose name was Wen, came during the Yongle reign from Hongdong County in Jin province. He was secretly registered in Pingmo township. Those of our ancestor's generation that remained in Jin have become lost. Although, those that remain in the home are separated from us by the war-ridden graves of generations, our ancestors' genealogical records have been revised in the hope of transmitting information accurately from generation to generation. However, there are doubts. There are small notes and prefaces under the names of each person that can be referenced. There is no need for the gentleman to write further.

Furthermore, our aim in this revision is to prioritize accuracy over style, and we will avoid using any flowery or embellished language. This genealogy, however, has a record of our blood relatives and their families. The lineages of these families are separate and can be traced to the record books. This will allow the descendants of our family to share harmony, promote kinship and family unity. And so, the descendants will follow this principle."

Commentary

Context: This text is likely a preface to a family genealogy. It outlines the history of the clan, particularly the circumstances of their migration during the early Ming dynasty. It also sets a tone for the importance of factual accuracy.

Historical References:

Sima Qian: The mention of the "Grand Historian" and the Records of the Grand Historian is a clear reference to Sima Qian, one of the most famous historians in Chinese history.

"Hereditary Houses" (世家): This refers to a specific section in the Records of the Grand Historian, which detailed the families of hereditary nobles and officials in ancient China.

Wei and Jin Dynasties (魏晋): This refers to the period of political division and social change that followed the collapse of the Han dynasty. During this time, family status played an important role in social mobility and influence.

Nine Rank System (九品中正): This was a system used in the Wei and Jin dynasties to select government officials based on their family background and social standing.

Liu Futong (劉福通): A leader of the Red Turban Rebellion during the late Yuan dynasty, whose rebellion caused widespread devastation.

Hongdong County (洪洞縣): During the Ming dynasty, there was a large-scale migration of people from Hongdong County in Shanxi province to fill in the depopulated areas throughout the empire, particularly after the chaos of the late Yuan.

Key Themes:

Importance of Family History: The text clearly shows the importance of knowing one's roots and maintaining family lineage.

Accuracy vs. Style: The author emphasizes the need for truthfulness in the genealogy, rather than embellishment or poetic language.

Preserving Family Unity: The genealogy serves to promote harmony and unity among clan members.

Confronting a history of loss and confusion: The clan is attempting to rectify and understand the family history after a period of major disruption.

Language and Style:

The text is written in classical Chinese, characterized by its concise style and literary allusions.

The author is clearly well-educated and familiar with the classics.

Let me know if you have any other questions about this fascinating piece of historical writing!
```



### 通义千问

![image-20250102220154149](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220154149.png)

![image-20250102215950208](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102215950208.png)





### Claude-3.5-Sonnet

错误挺多的：

![image-20250102223643321](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102223643321.png)

![image-20250102223706102](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102223706102.png)

### gpt-4o

![image-20250102224538875](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102224538875.png)

![image-20250102225025030](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102225025030.png)

### kimi

![image-20250102220219825](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220219825.png)

![image-20250102215937349](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102215937349.png)



### deepseek v3

![image-20250102220441384](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220441384.png)

![image-20250102220411581](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220411581.png)



### GLM

![image-20250102220103435](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220103435.png)

![image-20250102220131835](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220131835.png)

### 豆包

![image-20250102220014522](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220014522.png)

![image-20250102220004165](/images/20250102-ancient-chinese-texts-ai-analysis.assets/image-20250102220004165.png)


