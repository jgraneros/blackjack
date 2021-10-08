import sys
from PySide6 import QtCore, QtGui, QtWidgets
from functools import partial
from helpers import absPath
from cartas import *


class Jugador:
    def __init__(self, nombre):
        self.mano = []
        self.puntos = 0
        self.nombre = nombre
        self.plantado = False

    def sumar(self, carta):
        self.mano.append(carta)
        self.calcular()

    def calcular(self):
        self.puntos = 0
        # sumar cartas que no son ases y que sean visibles
        for carta in self.mano:
            if carta.visible:
                if carta.nombre not in ["As", "Jota", "Reina", "Rey"]:
                    self.puntos += carta.numero
                elif carta.nombre in ["Jota", "Reina", "Rey"]:
                    self.puntos += 10

        # sumamos los ases que sean visibles 
        for carta in self.mano:
            if carta.visible:
                 if carta.nombre == "As":
                     # sumaremos 11 si sumamos 21 puntos o menos
                     if self.puntos + 11 <= 21:
                         self.puntos += 11
                     else:
                         self.puntos += 1
    
    def consultar(self):
        print(f"{self.nombre}: {[f'{c.nombre} de {c.palo}'  for c in self.mano if c.visible]} ({self.puntos})")

class Blackjack:
    def __init__(self, baraja):
        self.baraja = baraja
        self.humano = Jugador("Juan")
        self.banca = Jugador("Banca")

    def repartir(self, jugador, voltear = True):
        carta = self.baraja.extraer()
        if carta:
            if voltear:
                carta.mostrar()
            # darsela al jugador
            jugador.sumar(carta)
        return carta

    def ganador(self):
        # devolvemos 0 si hay empate, 1 si gana el humano o 2 si gana la banca
        if self.humano.puntos > 21:
            return 2
        if self.banca.puntos > 21:
            return 1
        if self.humano.puntos > self.banca.puntos:
            return 1
        elif self.banca.puntos > self.humano.puntos:
            return 2
        else:
            return 0

    def comprobarGanador(self):
        ganador = self.ganador()
        if ganador == 2:
            print("Gana la banca")
        elif ganador == 1:
            print(" Gana el humano")
        else:
            print("Empate")

    def reiniciar(self):
        self.baraja.reiniciar()
        self.humano = Jugador("Juan")
        self.banca = Jugador("Banca")
        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # configuramos la ventana y el fondo
        self.setWindowTitle("Balckjack sin apuestas")
        self.setFixedSize(900, 630)
        # configuración de la baraja
        self.baraja = Baraja(self)
        self.setCentralWidget(self.baraja)
        # crear el juego blackjack
        self.bj = Blackjack(self.baraja)
        # interfaz (despues de asignar el widget central para sobreponerla)
        self.setupUi()
        # posicionamos las cartas y hacemos el reparto inicial
        self.preparar()

        self.btnPedir.clicked.connect(self.pedir)
        self.btnPlantar.clicked.connect(self.plantar)
        self.btnReiniciar.clicked.connect(self.reiniciar)
        self.finalizado = False

    def preparar(self):
        """Posiciona la baraja inicial y ejecuta los primeros repartos"""
        self.registro.append(f"== Empieza Blackjack ==")
        offset = 0
        for carta in self.baraja.cartas:
            carta.posicionar(45 + offset, 205 + offset)
            offset += 0.25

        # activar botones
        self.btnPedir.setEnabled(True)
        self.btnReiniciar.setEnabled(True)
        self.btnPlantar.setEnabled(True)
        self.repartir(self.bj.humano)
        self.repartir(self.bj.humano)
        self.repartir(self.bj.banca)
        self.repartir(self.bj.banca, voltear=False)


    def repartir(self, jugador, voltear=True):
        carta = self.bj.repartir(jugador, voltear)
        if jugador == self.bj.humano:
            offset_x = len(self.bj.humano.mano) * 40
            carta.mover(195+offset_x, 320, duracion=750)
        elif jugador == self.bj.banca:
            offset_x = len(self.bj.banca.mano) * 25
            carta.mover(251+offset_x, 110, duracion=750, escalado=0.8)
        self.marcadores()
    
    def pedir(self):
        self.btnPedir.setEnabled(False)
        self.btnReiniciar.setEnabled(False)
        self.btnPlantar.setEnabled(False)

        self.repartir(self.bj.humano)
        self.comprobar()

    def comprobar(self):
        self.btnReiniciar.setEnabled(True)
        # si el jugador humano tiene menos de 21 puntos le permitimos plantarse o pedir
        if self.bj.humano.puntos < 21:
            self.btnPedir.setEnabled(True)
            self.btnPlantar.setEnabled(True)
        # pero si tenemos 21 puntos o mas plantaremos al jugador y pasaremos a la banca
        if self.bj.humano.puntos >= 21:
            self.bj.humano.plantado = True
            # y aqui ejecutaremos el movimiento de la banca
            self.jugarBanca()



    def plantar(self):
        self.btnPedir.setEnabled(False)
        self.btnPlantar.setEnabled(False)
        self.bj.humano.plantado = True
        self.jugarBanca()

    def jugarBanca(self):
        if self.bj.humano.puntos > 21:
            self.bj.banca.plantado = True
        else:
            # si la banca tiene dos cartas voltearemos la segunda y calcularemos su puntuación
            if len(self.bj.banca.mano) == 2:
                self.bj.banca.mano[-1].mostrar()
                self.bj.banca.calcular()
                self.marcadores()
            # si la banca tiene 17 puntos o mas la plantamos
            # o si la banca tiene mas puntos que el jugador
            if self.bj.banca.puntos >= 17 or self.bj.banca.puntos > self.bj.humano.puntos:
                self.bj.banca.plantado = True
            # si la banca no se ha plantado le repartimos una carta
            if not self.bj.banca.plantado:
                self.repartir(self.bj.banca) 
                self.jugarBanca()
        self.ganador()


    def reiniciar(self):
        self.finalizado = False
        self.marcadorJugador.setText("0")
        self.marcadorBanca.setText("0")
        self.registro.setText("")
        self.bj.reiniciar()
        self.preparar()

    def marcadores(self):
        self.marcadorJugador.setText(f"{self.bj.humano.puntos}")
        self.marcadorBanca.setText(f"{self.bj.banca.puntos}")
        self.registro.append(f"{self.bj.humano.nombre} [{self.bj.humano.puntos}],{self.bj.banca.nombre} [{self.bj.banca.puntos}]")
        self.registro.verticalScrollBar().setValue(self.registro.verticalScrollBar().maximum())

    def ganador(self):
        if self.bj.humano.plantado and self.bj.banca.plantado and not self.finalizado:
            if self.bj.ganador() == 2:
                self.registro.append(f"== Ganador {self.bj.banca.nombre} ==")
            elif self.bj.ganador() == 1:
                self.registro.append(f"== Ganador {self.bj.humano.nombre} ==")
            else: 
                self.registro.append(f"===== Empate ======")
            self.registro.verticalScrollBar().setValue(self.registro.verticalScrollBar().maximum())
            self.finalizado = True

    def setupUi(self):
        self.setStyleSheet("""
            QTextEdit { background-color: #ddd; font-size: 13px }
            QLabel { color: white; font-size: 40px; font-weight: 500 }
            QPushButton { background-color: #20581e; color: white; font-size: 15px }
            QPushButton:disabled { background-color: #163914 }
        """)
        # configuracion del fondo
        tablero = QtGui.QImage("images/Tablero.png")
        paleta = QtGui.QPalette()
        paleta.setBrush(QtGui.QPalette.Window, QtGui.QBrush(tablero))
        self.setPalette(paleta)
        # marcadores
        self.marcadorBanca = QtWidgets.QLabel("0", self)
        self.marcadorBanca.resize(50, 50)
        self.marcadorBanca.move(342, 19)
        self.marcadorJugador = QtWidgets.QLabel("0", self)
        self.marcadorJugador.resize(50, 50)
        self.marcadorJugador.move(355, 557)
        # botones
        self.btnPedir = QtWidgets.QPushButton("Pedir carta", self)
        self.btnPedir.resize(175, 32)
        self.btnPedir.move(692, 495)
        self.btnPlantar = QtWidgets.QPushButton("Plantarse", self)
        self.btnPlantar.resize(175, 32)
        self.btnPlantar.move(692, 535)
        self.btnReiniciar = QtWidgets.QPushButton("Reiniciar", self)
        self.btnReiniciar.resize(175, 32)
        self.btnReiniciar.move(692, 575)
        # texto para el registro
        self.registro = QtWidgets.QTextEdit(self)
        self.registro.setReadOnly(True)
        self.registro.move(692, 285)
        self.registro.resize(175, 185)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # exec_() si PySide6 < 6.1.0 (pip install --upgrade pyside6)
    sys.exit(app.exec())
