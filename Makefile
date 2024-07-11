run:
	poetry run streamlit run src/main.py

lint:
	poetry run isort src
	poetry run black src -l 79
	poetry run flake8 src

unzip-fonts: fonts/IPAfont00303.zip
	cd fonts ; unzip -o IPAfont00303.zip

fonts/IPAfont00303.zip:
	wget https://moji.or.jp/wp-content/ipafont/IPAfont/IPAfont00303.zip -O fonts/IPAfont00303.zip