# ZafarXatlari Telegram bot

Bot buyurtmani ketma-ket yig‘adi va tasdiqlangandan keyin `ADMIN_CHAT_ID` ga yuboradi.

## Birinchi sozlash

1. Telegramda `@BotFather` ga kirib tokenni revoke qiling va yangi token oling. Eski token chatga yozilib ketgani uchun uni ishlatmaslik kerak.
2. PowerShellda loyiha papkasida tokenni faqat joriy terminal sessiyasiga kiriting:

```powershell
$env:BOT_TOKEN = 'YANGI_BOT_TOKEN'
```

3. Botni birinchi marta ishga tushiring:

```powershell
.\run_bot.ps1
```

4. Telegramda o‘zingiz yaratgan botga `/id` yuboring. Bot qaytargan raqamni nusxalang.
5. Botni to‘xtating va admin chat ID ni kiriting:

```powershell
$env:ADMIN_CHAT_ID = 'SIZNING_CHAT_ID'
.\run_bot.ps1
```

## 24/7 ishlatish

GitHub Pages saytni 24/7 beradi, lekin Python botni GitHub Pages ichida ishlata olmaydi. GitHub Actions ham doimiy server emas. Shu sabab bot uchun repository ichida `Dockerfile` va `railway.toml` bor: GitHub repository’ni Railway’ga ulab, botni doimiy worker sifatida ishlating.

Railway’da loyiha ochib, shu GitHub repository’ni tanlang. Variables bo‘limiga quyidagilarni qo‘ying, keyin Deploy bosing:

- `BOT_TOKEN`
- `ADMIN_CHAT_ID`

Railway yangi commit kelganda botni qayta deploy qiladi. `railway.toml` dagi `ALWAYS` siyosati process xato bilan yoki kutilmaganda to‘xtasa, uni qayta ishga tushiradi. Bu bot kompyuter o‘chiq bo‘lsa ham ishlashini ta’minlaydi. Railway hisobida worker ishlashi uchun tarif va billing cheklovlarini tekshiring; haqiqiy 24/7 uchun VPS yoki Railway’ning faol tarifi kerak bo‘lishi mumkin.

Bot kodi faqat `BOT_TOKEN` va `ADMIN_CHAT_ID` o‘zgaruvchilaridan foydalanadi. `PRICE_PER_LETTER` kerak emas.

## Sayt tugmasi

`index.html` ichidagi `https://t.me/zafarxatlari_bot` manzilini BotFather bergan haqiqiy bot username manziliga almashtiring.

Bot buyurtma xabarini faqat `ADMIN_CHAT_ID` ga yuboradi. Token va admin ID ni GitHub yoki frontend fayllariga joylamang.
