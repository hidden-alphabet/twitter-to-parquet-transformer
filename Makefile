AWS_USER_ID := $(shell aws sts get-caller-identity | jq '.["UserId"]' | tr -d '"')

ORG := hidden-alphabet
PROJECT := twitter-to-parquet
FN_NAME := $(ORG)-$(PROJECT)
FN_ROLE_ARN := arn:aws:iam::$(AWS_USER_ID):role/aws-lambda-cli-role
FN_BUNDLE := $(FN_NAME).zip

AWS_S3_BUCKET := $(ORG)
AWS_S3_KEY := functions

DEPS := dependencies

requirements.txt:
	pipenv lock -r > requirements.txt

$(DEPS): requirements.txt
	mkdir -p $(DEPS)
	pip download \
		--no-deps \
		--abi cp36m \
		--python-version 3 \
		--implementation cp \
		--platform manylinux1_x86_64 \
		-r requirements.txt \
		-d $(DEPS)
	cd $(DEPS) && unzip "*.whl" -d $(DEPS)
	cd $(DEPS) && \
		(rm -rf *.dist-info || true) && \
		(rm -rf __pycache__ || true)

$(FN_BUNDLE): $(DEPS)
	cd $(DEPS) && zip -r ../$(FN_BUNDLE) .
	zip -r $(FN_BUNDLE) ./hidden_alphabet

bundle: $(FN_BUNDLE)

build:
	docker cp $(shell docker create hidden_alphabet:$(PROJECT)-builder):/$(PROJECT)-transformer/$(FN_BUNDLE) .

profile:
	docker run hidden_alphabet:$(PROJECT)-profiler

deploy: build upload
	aws lambda create-function \
		--function-name $(FN_NAME) \
		--runtime python3.7 \
		--handler hidden_alphabet.aws.functions.twitter_search_html_to_parquet.handler\
		--timeout 60 \
		--role $(FN_ROLE_ARN) \
		--zip-file s3://$(AWS_S3_BUCKET)/$(AWS_S3_KEY)/$(FN_BUNDLE)

update: build
	aws lambda update-function-code \
		--function-name $(FN_NAME) \
		--zip-file s3://$(AWS_S3_BUCKET)/$(AWS_S3_KEY)/$(FN_BUNDLE)

upload: build
	aws s3 mv $(FN_BUNDLE) s3://$(AWS_S3_BUCKET)/$(AWS_S3_KEY)/$(FN_BUNDLE)

push: upload update

clean:
	rm -rf build
	rm $(FN_BUNDLE)
