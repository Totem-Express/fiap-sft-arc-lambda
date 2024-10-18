(ns totem-auth.core
  (:require [clojure.data.json :as json]
            [clojure.java.io :as io]
            [next.jdbc :as jdbc]
            [next.jdbc.result-set :as rs])
  (:import
   [com.auth0.jwt.algorithms Algorithm]
   [com.auth0.jwt JWT])
  (:gen-class
   :implements [com.amazonaws.services.lambda.runtime.RequestStreamHandler]))

;; Utils
(defn get-env [name fallback]
  (or (System/getenv name) fallback))

;; Database
(def database-property
  {:jdbcUrl (get-env "DB_URL" "jdbc:mysql://172.17.0.1:3307/totemexpress")
   :user (get-env "DB_USER" "totemexpress")
   :password (get-env "DB_PASSWORD" "secret")})

(def datasource (jdbc/get-datasource database-property))

(def find-user-query "SELECT id, name FROM user WHERE cpf = ?")

(defn find-user-by-cpf
  [cpf]
  (jdbc/execute-one! datasource
                     [find-user-query cpf]
                     {:builder-fn rs/as-unqualified-lower-maps}))

;; JWT
(def issuer "totem-express-auth")
(def secret "very-s3cr3t")
(def algorithm (Algorithm/HMAC256 secret))

(defn sign-jwt [{:keys [id name]}]
  (-> (JWT/create)
      (.withIssuer issuer)
      (.withPayload {"id" id "name" name})
      (.sign algorithm)))

;; Lambda
(def handle-error {:statusCode 400 :body "User not Found"})

(defn handle-success [jwt]
  {:statusCode 200
   :body jwt})

(defn handle-event [event]
  (if-let [user (some-> event :cpf find-user-by-cpf)]
    (->> user
         sign-jwt
         handle-success)
    handle-error))

(defn extract-request-body [request]
  (some-> request
          :body
          (json/read-str :key-fn clojure.core/keyword)))

;; This will be called from AWS Lambda
(defn -handleRequest [this is os context]
  (let [w (io/writer os)]
    (-> (json/read (io/reader is) :key-fn clojure.core/keyword)
        (extract-request-body)
        (handle-event)
        (json/write w))
    (.flush w)))

;; To Test Local in REPL
(defn create-input-stream
  "Create a input stream to test lambda"
  [filename]
  (->> (io/resource filename)
       (io/input-stream)
       (io/reader)))
