FROM freeradius/freeradius-server:latest-3.2

COPY clients.conf /opt/etc/raddb/clients.conf
COPY rest /opt/etc/raddb/mods-enabled/rest
COPY default /opt/etc/raddb/sites-enabled/default

# Clean up default inner-tunnel to avoid conflicts
RUN rm -f /opt/etc/raddb/sites-enabled/inner-tunnel

CMD ["radiusd", "-X"]
