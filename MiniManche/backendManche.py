from PyQt5.QtWidgets import QWidget
import pygame
import threading

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')



class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


class MancheRadio():
    def __init__(self, window):
        self.window = window
        self.thread_pygame = threading.Thread(target=self.runPygame,)
        self.done = False

    def startThread(self):
        self.thread_pygame.start()

    def stopThread(self):
        self.done = True
 
    def runPygame(self):
        pygame.init()

        # Définit la taille de la fenetre (largeur, hauteur).
        #screen = pygame.display.set_mode((500, 700))

        #pygame.display.set_caption("Manche")

        # Permet de savoir la vitesse de mise à jour des images de la fenetre.
        #clock = pygame.time.Clock()

        # Initialise le joystick.
        pygame.joystick.init()

        # Lancement de l'affichage des données.
        #textPrint = TextPrint()

        # -------- boucle principale -----------
        while not self.done:
            #
            # EVENT PROCESSING STEP
            #
            # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
            # JOYBUTTONUP, JOYHATMOTION
            for event in pygame.event.get(): # User did something.
                if event.type == pygame.QUIT: # If user clicked close.
                   self.done = True # Flag that we are done so we exit this loop.
                elif event.type == pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")
                    self.done = True
                elif event.type == pygame.JOYBUTTONUP:
                    print("Joystick button released.")
                    self.window.radio.onBoutonAPPush(None, True)

            #
            # DRAWING STEP
            #
            # First, clear the screen to white. Don't put other drawing commands
            # above this, or they will be erased with this command.
            #screen.fill(WHITE)
            #textPrint.reset()

            # Get count of joysticks.
            joystick_count = pygame.joystick.get_count()

            #textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
            #textPrint.indent()

            # For each joystick:
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()

                try:
                    jid = joystick.get_instance_id()
                except AttributeError:
                    # get_instance_id() is an SDL2 method
                    jid = joystick.get_id()
                #textPrint.tprint(screen, "Joystick {}".format(jid))
                #textPrint.indent()

                # Get the name from the OS for the controller/joystick.
                name = joystick.get_name()
                #textPrint.tprint(screen, "Joystick name: {}".format(name))

                try:
                    guid = joystick.get_guid()
                except AttributeError:
                    # get_guid() is an SDL2 method
                    pass
                else:
                    pass
                    #textPrint.tprint(screen, "GUID: {}".format(guid))

                # Usually axis run in pairs, up/down for one, and left/right for
                # the other.
                axes = joystick.get_numaxes()
                #textPrint.tprint(screen, "Number of axes: {}".format(axes))
                #textPrint.indent()

                self.window.pBrut = joystick.get_axis(0)
                #textPrint.tprint(screen, "Axis 0 value: {:>6.3f}".format(joystick.get_axis(0)))
                self.window.nzBrut = joystick.get_axis(1)
                #textPrint.tprint(screen, "Axis 1 value: {:>6.3f}".format(joystick.get_axis(1)))
                #textPrint.unindent()

                buttons = joystick.get_numbuttons()
                #textPrint.tprint(screen, "Number of buttons: {}".format(buttons))
                #textPrint.indent()

                for i in range(buttons):
                    button = joystick.get_button(i)
                    #textPrint.tprint(screen,
                                    #"Button {:>2} value: {}".format(i, button))
                #textPrint.unindent()
                #textPrint.unindent()

            #
            # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
            #

            # Go ahead and update the screen with what we've drawn.
            #pygame.display.flip()

            # Limit to 20 frames per second.
            #clock.tick(20)

        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        pygame.quit()




