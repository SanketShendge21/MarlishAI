# Translation Quality Test Results

**Date:** 2026-06-03 19:32
**Model:** NLLB-200 (check /health for exact variant)
**Tests:** 23/23 produced output

---

## marlish → english

### Test 1 ✅
- **Input:** `Aaj office madhe khup kaam hota, ekdum thaklo mi`
- **Devanagari:** आज office मध्ये खूप काम होत, एकदम थकलो मी
- **Got:** I was so tired from all the work I had to do at the office today.
- **Expected:** There was a lot of work in the office today, I'm very tired
- **Latency:** 683ms

### Test 2 ✅
- **Input:** `Udya amhi picnic la janar aahot, tu yeshil ka?`
- **Devanagari:** उद्या आम्ही पिकनिक ला जनर आहोत, तू येशिल क?
- **Got:** We're going to a picnic tomorrow, are you sure?
- **Expected:** We are going for a picnic tomorrow, will you come?
- **Latency:** 390ms

### Test 3 ✅
- **Input:** `Mala ek coffee de, khup thandi ahe baher`
- **Devanagari:** मला एक coffee दे, खूप ठंडी आहे बहेर
- **Got:** Give me a coffee, it's cold outside.
- **Expected:** Give me a coffee, it's very cold outside
- **Latency:** 313ms

### Test 4 ✅
- **Input:** `Tuza phone ka lagat nahi? Mi tula 10 vela call kela`
- **Devanagari:** तुझा phone का लगत नहि? मी तुला 10 वेल call केला
- **Got:** Why isn't your phone answering? I called you 10 times.
- **Expected:** Why isn't your phone connecting? I called you 10 times
- **Latency:** 711ms

### Test 5 ✅
- **Input:** `Jevayला काय बनवलं आज? mala bhuk lagli ahe`
- **Devanagari:** Jevayला काय बनवलं आज? मला भूक लागली आहे
- **Got:** What made Jevay today? I'm hungry.
- **Expected:** What did you cook for lunch today? I'm hungry
- **Latency:** 866ms

### Test 6 ✅
- **Input:** `Bhai paisa de, mala urgent lagto`
- **Devanagari:** भाई पैसा दे, मला उरगेनत लगतो
- **Got:** Give me the money, I feel urgent.
- **Expected:** Bro give me money, I need it urgently
- **Latency:** 694ms

### Test 7 ✅
- **Input:** `Mi exam pass zalo, khup khush ahe`
- **Devanagari:** मी exam pass ज़लो, खूप खुश आहे
- **Got:** I passed the exam, I'm very happy.
- **Expected:** I passed the exam, I'm very happy
- **Latency:** 819ms

### Test 8 ✅
- **Input:** `Ghari ye lavkar, aai vaat baghte ahe`
- **Devanagari:** घरी ये लवकर, आई वात बघते आहे
- **Got:** Come home early, Mom is watching the cattle.
- **Expected:** Come home early, mom is waiting
- **Latency:** 802ms

## hinglish → english

### Test 9 ✅
- **Input:** `Bhai aaj mera mood off hai, kuch mat bol`
- **Devanagari:** भाई आज मेरा मूड ऑफ है, कुछ मत बोल
- **Got:** Brother, I'm not in the mood today, don't say anything
- **Expected:** Bro my mood is off today, don't say anything
- **Latency:** 1124ms

### Test 10 ✅
- **Input:** `Kal exam hai aur maine kuch nahi padha`
- **Devanagari:** काल exam है और मैंने कुछ नाही पढ़ा
- **Got:** Tomorrow is the exam and I haven 't studied anything
- **Expected:** There's an exam tomorrow and I haven't studied anything
- **Latency:** 945ms

### Test 11 ✅
- **Input:** `Yaar wo movie dekhne chalte hain weekend pe`
- **Devanagari:** Yaar वो movie देखने चलते हैं वीकेंड पे
- **Got:** Yaar they go to the movies on weekends
- **Expected:** Dude let's go watch that movie on the weekend
- **Latency:** 752ms

### Test 12 ✅
- **Input:** `Mummy ne poha banaya hai, tu aa ja ghar pe`
- **Devanagari:** मम्मी ने पोहा बनाया है, तू आ जा घर पे
- **Got:** Mommy made a pot, you come home
- **Expected:** Mom made poha, come over to my house
- **Latency:** 724ms

### Test 13 ✅
- **Input:** `Bhai tera phone kidhar hai? Call nahi lag raha`
- **Devanagari:** भाई तेरा phone किधर है? Call नाही लग रहा
- **Got:** Brother, where is your phone?
- **Expected:** Bro where is your phone? The call isn't going through
- **Latency:** 634ms

### Test 14 ✅
- **Input:** `College mein aaj bahut boring tha, koi nahi aaya`
- **Devanagari:** College में आज बहुत boring थ, कोई नाही आया
- **Got:** College was very boring today, no one came
- **Expected:** College was very boring today, nobody came
- **Latency:** 777ms

## english → marlish

### Test 15 ✅
- **Input:** `I will come to your house tomorrow evening`
- **Devanagari:** मी उद्या संध्याकाळी तुझ्या घरी येईन.
- **Got:** mi udya sandhyakali tujhya ghari yeeena.
- **Expected:** Mi udya sandhyakali tuzhya ghari yein
- **Latency:** 828ms

### Test 16 ✅
- **Input:** `What time does the train leave?`
- **Devanagari:** ट्रेन किती वाजता निघते?
- **Got:** trena kiti vajata nighate?
- **Expected:** Train kadhi sutte?
- **Latency:** 654ms

### Test 17 ✅
- **Input:** `Please send me the photos from yesterday`
- **Devanagari:** कृपया मला कालचे फोटो पाठवा.
- **Got:** krupaya mala kalache photo pathava.
- **Expected:** Mala kalche photos pathav
- **Latency:** 688ms

## english → hinglish

### Test 18 ✅
- **Input:** `I will come to your house tomorrow evening`
- **Devanagari:** मैं कल शाम को तुम्हारे घर आऊंगा
- **Got:** main kala shama ko tumhare ghar aaoonga
- **Expected:** Main kal shaam ko tere ghar aaunga
- **Latency:** 736ms

### Test 19 ✅
- **Input:** `The food was really delicious`
- **Devanagari:** खाना बहुत स्वादिष्ट था
- **Got:** khana bahuta svadishta tha
- **Expected:** Khana bahut tasty tha
- **Latency:** 463ms

## marathi → english

### Test 20 ✅
- **Input:** `मला आज ऑफिसला जायचं नाही, खूप थकवा आलाय`
- **Got:** I don't want to go to the office today, I'm very tired.
- **Expected:** I don't want to go to the office today, I'm very tired
- **Latency:** 1309ms

### Test 21 ✅
- **Input:** `तुझा भाऊ काय करतो? तो कुठे राहतो?`
- **Got:** What does your brother do? Where does he live?
- **Expected:** What does your brother do? Where does he live?
- **Latency:** 835ms

## hindi → english

### Test 22 ✅
- **Input:** `मुझे आज बहुत नींद आ रही है, रात को सो नहीं पाया`
- **Got:** I'm sleepy today, I couldn't sleep last night.
- **Expected:** I'm very sleepy today, I couldn't sleep last night
- **Latency:** 1142ms

### Test 23 ✅
- **Input:** `क्या तुम कल मेरे साथ बाजार चलोगे?`
- **Got:** Will you go shopping with me tomorrow?
- **Expected:** Will you come to the market with me tomorrow?
- **Latency:** 671ms

---

## Summary

- 23/23 tests produced non-empty translations
- Review each result above to assess semantic accuracy
