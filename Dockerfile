FROM archlinux
RUN pacman -Sy
RUN pacman -S wget apitrace python-pip gunicorn --noconfirm
RUN yes | pip install valvetraces Flask
RUN /usr/bin/wget flightlessmango.com/http_server.py
CMD ["gunicorn", "--workers", "1", "--threads", "4", "http_server:app"]