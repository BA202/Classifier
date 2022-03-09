import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# for text preprocessing
from io import StringIO
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer


class CategoryClassifier:
    def __init__(self, training_data):
        """
        Here a Tf-idf vectorizer is used to vectorize the cleaned data
        A Multinomial Naive Bayes Classifier is here used to fit the vectorized data

        Parameters
        ----------
        training_data : list
            contains as first string the full review and for the second string the associated category
            [[string, string]]
        """
        self.__category_dict = {
            "Location": 1,
            "Room": 2,
            "Food": 3,
            "Staff": 4,
            "ReasonForStay": 5,
            "GeneralUtility": 6,
            "HotelOrganisation": 7,
            "Unknown": 8,
        }

        self.__inv_category_dict = {v: k for k, v in self.__category_dict.items()}

        cleaned_training_data = []
        for sent in training_data:
            sent_list = [
                self.__preprocess_sentences(sent[0]),
                self.__category_dict[sent[1]],
            ]
            cleaned_training_data.append(sent_list)

        df_train = pd.DataFrame(cleaned_training_data, columns=["sentence", "category"])
        X_train = df_train["sentence"]
        y_train = df_train["category"]

        self.__tfidf_vec = TfidfVectorizer(use_idf=True)
        X_train_vec_tfidf = self.__tfidf_vec.fit_transform(
            X_train
        )  # tfidf runs on non-tokenized sentences unlike word2vec

        self.__nb_tfidf = MultinomialNB()
        self.__nb_tfidf.fit(X_train_vec_tfidf, y_train)

    def __preprocess_sentences(self, string):
        """

        Parameters
        ----------
        string

        Returns
        -------
        string

        Examples
        --------

        """
        text = string.lower().replace(".", " ").replace(",", " ")

        a = [word for word in text.split() if word not in stopwords.words("english")]
        no_stopwords_txt = " ".join(a)

        snow = SnowballStemmer("english")
        b = [snow.stem(word) for word in word_tokenize(no_stopwords_txt)]
        stemmed_txt = " ".join(b)

        wordnet_lemmatizer = WordNetLemmatizer()
        c = [wordnet_lemmatizer.lemmatize(word) for word in stemmed_txt.split(" ")]
        lemmatized_txt = " ".join(c)

        return lemmatized_txt

    def classify(self, string):
        """
        Returns a list with the predicted category and the certainty of the prediction

        A Tf-idf vectorizer is used to vectorize the string
        For the prediction the pre-trained Multinomial Naive Bayes Classifier is used

        Parameters
        ----------
        string

        Returns
        -------
        list
            [(string, float)]
        """
        cleaned_string = self.__preprocess_sentences(string)
        cleaned_string = StringIO(cleaned_string)

        df_test = pd.DataFrame(cleaned_string, columns=["sentence"])
        X_test = df_test["sentence"]

        X_test_vec_tfidf = self.__tfidf_vec.transform(X_test)
        y_predict_test = self.__nb_tfidf.predict(X_test_vec_tfidf)
        y_proba_test = self.__nb_tfidf.predict_proba(X_test_vec_tfidf)[:, 1]

        df_test["predicted_category"] = y_predict_test
        df_test["confidence"] = y_proba_test

        predicted_category = df_test["predicted_category"].tolist()
        confidence = df_test["confidence"].tolist()
        full_list = list(zip(predicted_category, confidence))

        result_list = []
        for sent in full_list:
            sentence_list = [self.__inv_category_dict[sent[0]], sent[1]]
            result_list.append(sentence_list)

        return result_list


if __name__ == "__main__":
    from DataHandler.DataHandler import DataHandler
    from sklearn.model_selection import train_test_split

    my_data_handler = DataHandler()
    category_list = my_data_handler.getCategorieData("Location")
    #   for sent in category_list[1:10]:
    #     print(f"{sent[0]:100}|{sent[1]}")

    training_data, test_data = train_test_split(
        category_list, test_size=0.2, shuffle=True
    )

    txt = "The staff was very friendly"

    classifier = CategoryClassifier(training_data)
    res = classifier.classify(txt)
    print(res)
