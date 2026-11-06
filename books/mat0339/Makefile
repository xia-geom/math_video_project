.PHONY: all manual student answers verify verify-video-map release
all:
	python3 scripts/build.py all
manual:
	python3 scripts/build.py manual
student:
	python3 scripts/build.py student
answers:
	python3 scripts/build.py answers
verify:
	python3 scripts/verify.py
verify-video-map:
	python3 scripts/video_map.py
	python3 -m unittest discover -s integration_tests -v
release:
	python3 scripts/build.py all --release
