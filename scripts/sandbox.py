from napalm import get_network_driver



def main():
    driver = get_network_driver('nxos_ssh')

    with driver('172.20.22.62', 'wamer', 'Weda711;') as device:
        print(device.get_interfaces())



if __name__ == "__main__":
    main()