# USE CASE DOCUMENTATION & CHAT SIMULATION AI-UMROH (SLEEK & FAST CLOSING)

This documentation simulates a WhatsApp conversation between a Pilgrim (Pilgrim) and the AI Sales Agent (AI) with a highly friendly, concise, solution-oriented tone, directly providing recommendations and sending PDF Invoices directly inside the chat (frictionless).

---

## SCENARIO 1: Package Inquiry, Recommendation, and PDF Invoice Sending

This scenario demonstrates a fast closing flow starting from asking about the economy package, recommending the best option, requesting brief manifest data, sending the PDF Invoice, and ending with payment confirmation.

* **DB Payment Status**: `POTENTIAL`
* **Bot Mode**: `SALES_MODE`

```
[Pilgrim] : Assalamualaikum, I want to ask about the cheapest umrah package for the end of this year.

[AI]      : Wa'alaikumsalam Warahmatullahi Wakarakatuh, Brother/Sister! Welcome to Berkah Umroh Internasional registration services. I am Salsa, ready to assist your holy journey to the Baitullah. 🕋✨

            For the end of this year, Salsa highly recommends our Berkah Umroh Package (Economy). The facilities are very comfortable even though the price is incredibly budget-friendly:
            ✈️ Saudia Airlines (Direct flight, no transit)
            🏨 3-Star Hotel (Close distance, ±300m from the mosque)
            💰 Price starts from IDR 28,500,000 per person (All-In).

            Are you planning to travel alone, or are you planning to bring your beloved family along, Brother/Sister? 😊

[Pilgrim] : I'm going with my wife. Can I book first?

[AI]      : Masya Allah, alhamdulillah! It will certainly be a more memorable and romantic pilgrimage going with your beloved wife. May Allah ease your good intentions and your wife's. 🤲🌸

            Of course you can! To secure your seats and make sure they aren't taken by other pilgrims, you can lock your seat today with a Down Payment (DP) of only IDR 5,000,000 per person.

            May Salsa help register you first? Simply send this brief data:
            
            Full Name (as on ID card):
            Number of Participants: 2 People
            City of Origin:

[Pilgrim] : Full Name: Ahmad Fauzi & Siti Aminah
            Number of Participants: 2 People
            City of Origin: Bandung

[AI]      : Excellent Brother Ahmad, your data has been received and secured in our system.

            Your Booking:
            📦 Berkah Umroh Package (2 Pax)
            💰 Total DP: IDR 10,000,412 (Including transaction unique code)

            Here is your official Invoice. Please transfer the exact amount listed to the official PT Berkah Umroh Internasional BSI account shown in the Invoice: 🙏

            📄 INV-UMROH-1002.pdf
            [PDF Document Attached]

            Once the transfer is complete, could you please send a photo of the transfer proof here? Thank you!

[Pilgrim] : (Sends Transfer Proof Photo from Mobile Banking for IDR 10,000,412)
            I have transferred it just now.

[AI]      : Thank you so much, Brother Ahmad! 🙏
            We have successfully received and verified your DP payment of IDR 10,000,412 in our financial system. The flight seats for Brother Ahmad and Sister Siti Aminah are now officially locked and secured.

            After this, our admin team will reach out to assist you with physical document preparations such as passports. Enjoy preparing for your best worship journey! ✨🌸
```

---

## SCENARIO 2: Handling Objection regarding Legitimacy

A short and reassuring scenario when a pilgrim feels anxious about the safety and legitimacy of the travel agency.

```
[Pilgrim] : But is this travel agency really safe? There are so many scam umrah travel agencies nowadays, I'm a bit afraid to transfer.

[AI]      : Salsa completely understands your concern. It is very natural because this worship fund was gathered with holy intentions and extraordinary hard work. Safety is definitely number one, Brother/Sister. 😊

            To make you feel more at ease and confident, here are our security guarantees:

            1. Ministry of Religious Affairs (Kemenag) License: PT Berkah Umroh Internasional is officially registered as an Umrah Pilgrimage Organizer (PPIU) with License No. 9120002131. You can check it directly in the Kemenag Pusaka app.
            2. Official Corporate Account: We never accept transfers to personal accounts. All payments must go to our official corporate account under PT Berkah Umroh Internasional.
            3. Physical Office: Our office is located at Jl. Asia Afrika No. 123, Bandung. Our doors are always open if you or your family would like to visit and have a warm chat first. 🌸

            Is there anything else that makes you hesitant? Salsa is ready to help clarify further with pleasure. 🙏
```

---

## SCENARIO 3: Restricting Conversation Topics (Strict Guardrails)

A polite and gentle rejection scenario when the pilgrim goes out of the context of umrah sales.

```
[Pilgrim] : Salsa, will it rain in Bandung tomorrow? I need to pick up my kid from school.

[AI]      : Weather changes in Bandung have indeed been quite frequent lately. May tomorrow's weather be friendly and your journey to pick up your child always be given safety and smoothness by Allah SWT. Don't forget to keep an umbrella in your vehicle! 🌧️😊

            Regarding weather forecasting, we apologize as Salsa does not have direct real-time access to the local BMKG radar.

            As a virtual assistant for umrah journeys, Salsa is designed specifically to help facilitate your registration and preparation for worship to the holy lands of Mecca and Medina. 🕋

            If you have any questions regarding umrah packages, facility details, or departure schedules, please feel free to ask Salsa directly! 🙏
```
