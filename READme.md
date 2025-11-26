# Budget Buddy - Smart Expense Tracker 💰

A professional AI-powered budget tracking application that uses Google's Gemini AI to automatically classify and extract expenses from bill images.

## Features ✨

- 🎯 **Smart Onboarding**: Set up your income and budget categories
- 📸 **Camera Integration**: Capture bills directly from your device camera
- 📁 **Gallery Upload**: Upload existing bill images
- 🤖 **AI-Powered Classification**: Automatically categorizes expenses using Gemini AI
- 💵 **Expense Extraction**: Extracts amounts from bills automatically
- 📊 **Visual Dashboard**: Beautiful charts and progress tracking
- 💾 **SQLite Database**: Local data storage
- 📋 **ITR Ready**: Store all bills for tax filing purposes
- 🎨 **Professional UI**: Modern, responsive design

## Categories Supported

- 🏠 Rent
- 🍔 Food
- 👕 Clothing
- 💻 Electronics
- ✈️ Travel
- ⚕️ Medical
- 🎉 Discretionary

## Tech Stack

**Backend:**
- Python 3.8+
- Flask
- SQLite
- Google Gemini AI
- PIL (Image Processing)

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js
- Camera API

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Step 1: Clone or Download Files

Create a project folder and ensure you have these files:
```
budget-buddy/
├── app.py
├── index.html
├── requirements.txt
├── .env
└── README.md
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. Create a `.env` file in the project root
2. Add your Google Gemini API key:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 5: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Use 📱

### First Time Setup (Onboarding)

1. **Enter Monthly Income**: Input your total monthly income
2. **Set Budget Categories**: Allocate budget for each expense category
3. **Click "Start Tracking"**: Complete onboarding and access dashboard

### Daily Usage

1. **Capture Bill**: 
   - Click "📷 Capture Bill" to use your camera
   - Take a photo of your receipt/bill
   - AI will automatically classify and extract the amount

2. **Upload from Gallery**:
   - Click "📁 Upload from Gallery"
   - Select an existing bill image
   - AI processes and categorizes it

3. **Monitor Budget**:
   - View real-time spending in each category
   - Check remaining budget with visual progress bars
   - Analyze spending with pie chart

4. **Access Bills Archive**:
   - All bills are stored with images
   - Hover over bills to see details
   - Delete bills if needed
   - Share with CA for ITR filing

## API Endpoints 🔌

### `POST /api/onboard`
Create initial budget setup
```json
{
  "income": 50000,
  "expenses": {
    "rent": 15000,
    "food": 10000,
    "clothing": 5000,
    "electronics": 3000,
    "travel": 5000,
    "medical": 2000,
    "discretionary": 5000
  }
}
```

### `GET /api/budget`
Fetch current budget data

### `POST /api/upload_bill`
Upload and analyze a bill image
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

### `GET /api/bills`
Get all stored bills

### `DELETE /api/delete_bill/<id>`
Delete a specific bill

### `POST /api/reset`
Reset all data (caution!)

## Database Schema 📊

### user_budget table
- id (PRIMARY KEY)
- income
- rent_budget, rent_spent
- food_budget, food_spent
- clothing_budget, clothing_spent
- electronics_budget, electronics_spent
- travel_budget, travel_spent
- medical_budget, medical_spent
- discretionary_budget, discretionary_spent
- created_at

### bills table
- id (PRIMARY KEY)
- image_data (Base64 encoded)
- category
- amount
- description
- date
- created_at

## AI Classification Prompt

The app uses Google Gemini AI with a specialized prompt to:
1. Identify the expense category
2. Extract the total amount
3. Generate a brief description

The AI is trained to recognize:
- Restaurant bills → Food
- Rent receipts → Rent
- Medical prescriptions → Medical
- Fuel bills → Travel
- Shopping receipts → Clothing/Electronics
- And more...

## Troubleshooting 🔧

### Camera Not Working
- Grant camera permissions in browser
- Use HTTPS or localhost (camera requires secure context)
- Try "Upload from Gallery" as alternative

### AI Classification Incorrect
- Ensure bill image is clear and well-lit
- Check that text on bill is readable
- Manually verify amounts in dashboard

### Database Issues
- Delete `budget_tracker.db` to reset
- Or use `/api/reset` endpoint

## Security Notes 🔒

- API key stored in `.env` (never commit to git)
- Add `.env` to `.gitignore`
- Data stored locally in SQLite
- No external data transmission except Gemini API

## Future Enhancements 🚀

- [ ] Multi-user support with authentication
- [ ] Monthly/Yearly reports
- [ ] Export to PDF for ITR
- [ ] Budget recommendations using AI
- [ ] Recurring expense detection
- [ ] Mobile app version
- [ ] Cloud backup

## Credits

Built with ❤️ using:
- Google Gemini AI
- Flask
- Chart.js
- Modern Web APIs

## License

MIT License - Feel free to use and modify!

---

**Note**: This is a single-user application. For production use with multiple users, add authentication and user management.