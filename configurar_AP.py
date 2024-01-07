import subprocess
import time

def update_dependencies():
    print("[+] Actualizando e instalando dependencias...")
    subprocess.run(["sudo", "apt-get", "update"])
    subprocess.run(["sudo", "apt-get", "install", "dnsmasq", "hostapd", "-y"])

def configure_dnsmasq(ap_iface):
    print("[+] Configurando dnsmasq...")
    dnsmasq_config = f"""
    interface={ap_iface}
    dhcp-range=10.0.0.3,10.0.0.20,12h
    """
    with open("/etc/dnsmasq.conf", "w") as file:
        file.write(dnsmasq_config)

def configure_hostapd(ap_iface, ssid, channel, wpa_passphrase=None):
    print("[+] Configurando hostapd...")
    hostapd_config = f"""
    interface={ap_iface}
    ssid={ssid}
    channel={channel}
    """
    if wpa_passphrase:
        hostapd_config += f"\nwpa=2\nwpa_passphrase={wpa_passphrase}\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\n"
    
    with open("/etc/hostapd/hostapd.conf", "w") as file:
        file.write(hostapd_config)

def configure_iptables(ap_iface, net_iface):
    print("[+] Configurando iptables...")
    subprocess.run(["sudo", "iptables", "--flush"])
    subprocess.run(["sudo", "iptables", "--table", "nat", "--flush"])
    subprocess.run(["sudo", "iptables", "--delete-chain"])
    subprocess.run(["sudo", "iptables", "--table", "nat", "--delete-chain"])
    subprocess.run(["sudo", "iptables", "--table", "nat", "--append", "POSTROUTING", "--out-interface", net_iface, "-j", "MASQUERADE"])
    subprocess.run(["sudo", "iptables", "--append", "FORWARD", "--in-interface", ap_iface, "-j", "ACCEPT"])

def start_access_point(ap_iface):
    print("[+] Iniciando punto de acceso...")
    subprocess.run(["sudo", "ifconfig", ap_iface, "up", "10.0.0.1", "netmask", "255.255.255.0"])
    subprocess.run(["sudo", "service", "dnsmasq", "start"])
    subprocess.run(["sudo", "service", "hostapd", "start"])

def stop_access_point():
    print("[+] Deteniendo punto de acceso...")
    subprocess.run(["sudo", "service", "dnsmasq", "stop"])
    subprocess.run(["sudo", "service", "hostapd", "stop"])

def main():
    ap_iface = input("Ingrese el nombre de la interfaz inalámbrica para el AP: ")
    ssid = input("Ingrese el SSID para el AP: ")
    channel = input("Ingrese el canal para el AP: ")
    wpa_passphrase = input("¿Desea configurar una contraseña para el AP? (deje en blanco para omitir): ")
    
    print("Configurando punto de acceso Wi-Fi en Raspberry Pi")
    update_dependencies()
    configure_dnsmasq(ap_iface)
    configure_hostapd(ap_iface, ssid, channel, wpa_passphrase)
    configure_iptables(ap_iface, net_iface)
    
    start_ap = input("¿Iniciar el punto de acceso? (Y/n): ")
    if start_ap.lower() == "y" or start_ap == "":
        start_access_point(ap_iface)
        print("El punto de acceso se ha iniciado. Presiona Ctrl+C para detenerlo.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_access_point()
            print("El punto de acceso se ha detenido.")

if __name__ == "__main__":
    main()
