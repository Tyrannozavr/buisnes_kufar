# Gotenberg + Times New Roman для DOCX→PDF (LibreOffice).
# Шрифты: TeX Gyre Termes (GUST, свободная лицензия) + fontconfig alias «Times New Roman».
FROM gotenberg/gotenberg:8

USER root

RUN apt-get update \
	&& apt-get install -y --no-install-recommends fontconfig \
	&& rm -rf /var/lib/apt/lists/*

COPY fonts/texgyretermes-regular.otf \
	fonts/texgyretermes-bold.otf \
	fonts/texgyretermes-italic.otf \
	fonts/texgyretermes-bolditalic.otf \
	/usr/share/fonts/truetype/tex-gyre-termes/

COPY fonts/GUST-FONT-LICENSE.txt /usr/share/fonts/truetype/tex-gyre-termes/
COPY fonts/99-times-new-roman.conf /etc/fonts/local.conf

RUN fc-cache -f -v

USER gotenberg
