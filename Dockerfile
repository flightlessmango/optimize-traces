FROM archlinux
RUN pacman -Sy
RUN pacman -S wget apitrace python-pip --noconfirm
RUN yes | pip install valvetraces Flask gunicorn
RUN wget flightlessmango.com/http_server.py
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 http_server:app