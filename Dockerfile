FROM archlinux
RUN pacman -Sy
RUN pacman -S wget apitrace python-pip gunicorn --noconfirm
RUN yes | pip install valvetraces Flask
RUN wget flightlessmango.com/http_server.py
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 http_server:app