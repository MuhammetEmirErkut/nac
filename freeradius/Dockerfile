FROM freeradius/freeradius-server:latest-3.2

COPY clients.conf /etc/freeradius/clients.conf
COPY rest /etc/freeradius/mods-enabled/rest
COPY default /etc/freeradius/sites-enabled/default

# Clean up defaults to avoid conflicts with our custom sites
RUN rm -f /etc/freeradius/sites-enabled/inner-tunnel && \
    rm -f /etc/freeradius/mods-enabled/eap
