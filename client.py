import asyncio
import logging
import argparse

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


async def ricevi(reader, writer):
    while True:
        dati = await reader.readline()
        if not dati:
            if not writer.is_closing():
                logging.info("Server disconnesso. Premere invio per uscire.")
                writer.close()
            break
        logging.info(dati.decode().strip())


async def invia(writer):
    while True:
        testo = await asyncio.to_thread(input)
        if testo == "QUIT" or writer.is_closing():
            break
        writer.write((testo + "\n").encode())
        await writer.drain()
    writer.close()


async def main():
    host = "127.0.0.1"

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port to connect to")
    args = parser.parse_args()

    try:
        if args.port:
            reader, writer = await asyncio.open_connection(host, int(args.port))
            logging.info("Connesso al broker. Digitare 'QUIT' per uscire")
        else:
            logging.error("Porta non specificata")

        await asyncio.gather(ricevi(reader, writer), invia(writer))
    except ValueError:
        logging.error("La porta deve essere un numero")


asyncio.run(main())