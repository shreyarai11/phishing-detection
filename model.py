import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def extract_features(url):
    return [
        len(url),
        url.count('.'),
        url.count('-'),
        int('https' in url),
    ]

data = pd.read_csv("dataset.csv")

X = data['url'].apply(extract_features).tolist()
y = data['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

def predict_url(url):
    features = [extract_features(url)]
    result = model.predict(features)[0]
    return "Phishing ⚠️" if result == 1 else "Safe ✅"