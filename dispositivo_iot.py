import asyncio
import logging
import random

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

class Broker:

    stato_LED = "OFF"

    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port

    async def pubblica(self, writer, messaggio):

        print(f"[PUBBLICAZIONE]: {messaggio}")
        try:
            writer.write(f"OK {messaggio}\n".encode())
            await writer.drain()
        except ConnectionError:
            print("[ERRORE] Invio fallito")

    async def esegui_comando(self, comando, writer, indirizzo):

        if comando == "TEMP":
            n = random.uniform(20.0, 27.0)
            messaggio = str(n) + "C"
            await self.pubblica(writer, messaggio)
        elif comando == "UMIDITA":
            n = random.uniform(0, 100)
            messaggio = str(n)+"%"
            await self.pubblica(writer, messaggio)
        elif comando == "LED ON":
            self.stato_LED = "ON"
            messaggio = self.stato_LED
            await self.pubblica(writer, messaggio)
        elif comando == "LED OFF":
            self.stato_LED = "OFF"
            messaggio = self.stato_LED
            await self.pubblica(writer, messaggio)
        elif comando == "STATO":
            n = random.uniform(20.0, 27.0)
            nn = random.uniform(0, 100)
            messaggio = str(n) + "C - " + str(nn) + "% - LED" + self.stato_LED
            await self.pubblica(writer, messaggio)
        elif comando == "QUIT":
            logging.info(f"[DISCONNESSIONE] {indirizzo}")
            writer.close()
            await writer.wait_closed()
        else:
            logging.error(f"[ERRORE] Comando sconosciuto: {comando}")

    async def gestisci_client(self, reader, writer):
        indirizzo = writer.get_extra_info("peername")
        logging.info(f"[CONNESSIONE] {indirizzo}")

        try:
            while True:
                dati = await reader.readline()
                if not dati:
                    break
                comando = dati.decode().strip()
                print(comando)
                logging.info(f"[RICEVUTO] {comando} da {indirizzo}")
                await self.esegui_comando(comando, writer, indirizzo)
        except ConnectionError:
            pass
        finally:
            logging.info(f"[DISCONNESSIONE] {indirizzo}")
            writer.close()
            await writer.wait_closed()

    async def avvia(self):
        server = await asyncio.start_server(self.gestisci_client, self.host, self.port)
        logging.info(f"[BROKER] In ascolto su {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    broker = Broker()
    try:
        asyncio.run(broker.avvia())
    except KeyboardInterrupt:
        logging.info("[STOP] Broker interrotto")