FROM archlinux
RUN pacman -Sy
RUN pacman -S wget apitrace python-pip --noconfirm
RUN yes | pip install valvetraces
RUN wget flightlessmango.com/http_server.py
CMD python http_server.py