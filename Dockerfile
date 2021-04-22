FROM archlinux
RUN pacman -Sy
RUN pacman -S apitrace python-pip --noconfirm
RUN yes | pip install valvetraces