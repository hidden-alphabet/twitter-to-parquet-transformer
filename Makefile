AWS_USER_ID := $(shell aws sts get-caller-identity | jq '.["UserId"]' | tr -d '"')

FN_NAME := hidden-alphabet-twitter-html-to-parquet
FN_ROLE_ARN := arn:aws:iam::$(AWS_USER_ID):role/aws-lambda-cli-role
FN_BUNDLE := $(FN_NAME).zip

AWS_S3_BUCKET := hidden-alphabet
AWS_S3_KEY := functions

DEPS := build

requirements.txt:
	pipenv lock -r > requirements.txt

$(DEPS): requirements.txt
	mkdir -p $(DEPS)
	pip3 install \
		--no-deps \
		--abi cp36m \
		--python-version 3 \
		--implementation cp \
		--platform manylinux1_x86_64 \
		-r requirements.txt \
		-t $(DEPS)
	cd $(DEPS) && rm -r *.dist-info __pycache__

$(FN_BUNDLE): $(DEPS)
	cd $(DEPS) && zip -r ../$(FN_BUNDLE) .
	zip -r $(FN_BUNDLE) ./hidden_alphabet
	cd hidden_alphabet/aws/functions && \
		zip -r ../../../$(FN_BUNDLE) ./twitter_search_html_to_parquet.py

bundle: $(FN_BUNDLE) 

deploy: $(FN_BUNDLE) 
	aws lambda create-function \
		--function-name $(FN_NAME) \
		--runtime python3.7 \
		--handler twitter_search_html_to_parquet.handler\
		--timeout 60 \
		--role $(FN_ROLE_ARN) \
		--zip-file fileb://$(FN_BUNDLE)

update: $(FN_BUNDLE)
	aws lambda update-function-code \
		--function-name $(FN_NAME) \
		--zip-file fileb://$(FN_BUNDLE)

upload: $(FN_BUNDLE)
	aws s3 mv $(FN_BUNDLE) s3://$(AWS_S3_BUCKET)/$(AWS_S3_KEY)/$(FN_BUNDLE) 

clean:
	rm -rf build
	rm $(FN_BUNDLE)
