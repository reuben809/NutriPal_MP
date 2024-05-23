# NutriPal: Your AI-Powered Nutrition Coach

NutriPal is an AI-powered nutrition coach designed to help users make informed decisions about their diet and wellness. It leverages cutting-edge natural language processing and computer vision technologies to provide personalized recommendations and insights tailored to each user's unique health profile and dietary preferences.

## Features

- **Image-Based Ingredient Detection:** Users can upload images of ingredients, and NutriPal will identify them using state-of-the-art image classification models.
  
- **Health Profile Integration:** NutriPal takes into account each user's health history and dietary restrictions when generating recipe recommendations.
  
- **Environmental Considerations:** Users can opt to prioritize environmentally friendly ingredients and recipes, helping reduce their carbon footprint while promoting sustainable eating habits.

- **User Authentication:** NutriPal offers secure user authentication and account management functionalities to ensure data privacy and confidentiality.

## Installation

To install and run NutriPal locally, follow these steps:

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/YourUsername/NutriPal.git
   ```

2. Install the required dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   - Create a `.env` file in the project root directory.
   - Define the required environment variables in the `.env` file, such as MongoDB connection string and Hugging Face API key.

4. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

## Usage

1. Navigate to the Streamlit app URL in your web browser.
2. Log in or sign up for a NutriPal account.
3. Upload images of ingredients or manually enter your kitchen inventory.
4. Specify any health concerns or dietary preferences.
5. Generate personalized recipe recommendations based on your inputs.

## Contributing

Contributions are welcome! If you encounter any bugs, have feature requests, or want to contribute improvements, please open an issue or submit a pull request.

