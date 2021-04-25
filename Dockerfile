FROM archlinux
RUN pacman -Sy
RUN pacman -S wget apitrace python-pip gunicorn --noconfirm
RUN yes | pip install valvetraces Flask
RUN /usr/bin/wget flightlessmango.com/http_server.py
# CMD /usr/bin/gunicorn --bind :8080 --workers 1 --threads 1 --timeout 0 http_server:app
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--timout", "0", "http_server:app"]