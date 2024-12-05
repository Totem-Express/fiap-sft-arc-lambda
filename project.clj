(defproject totem-auth "1.0"
  :description "Lambda de autenticação para o projeto da pós graduação em Arquitetura de Software na FIAP"
  :url "https://postech.fiap.com.br/"
  :dependencies [;; Clojure
                 [org.clojure/clojure "1.11.1"]
                 [org.clojure/data.json "2.5.0"]
                 ;; Aws Lambda 
                 [com.amazonaws/aws-lambda-java-events "3.12.0"]
                 [com.amazonaws/aws-lambda-java-core "1.2.3"]
                 ;; Database
                 [com.github.seancorfield/next.jdbc "1.3.955"]
                 [com.mysql/mysql-connector-j "9.1.0"]
                 ;; JWT
                 [com.auth0/java-jwt "4.4.0"]]
  :main ^:skip-aot lambda.core.LambdaHandler
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}}
  :repl-options {:init-ns totem-auth.core})
