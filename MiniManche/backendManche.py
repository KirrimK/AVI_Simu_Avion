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
        self.thread_pygame.start()

    def stopThread(self):
        self.done = True
 
    def runPygame(self):
        pygame.init()

        # Définit la taille de la fenetre (largeur, hauteur).
        screen = pygame.display.set_mode((500, 700))

        pygame.display.set_caption("Manche")

        # Permet de savoir la vitesse de mise à jour des images de la fenetre.
        clock = pygame.time.Clock()

        # Initialise le joystick.
        pygame.joystick.init()

        # Lancement de l'affichage des données.
        textPrint = TextPrint()

        # -------- boucle principale -----------
        while not self.done:
            #
            # EVENT PROCESSING STEP
            #
            # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
            # JOYBUTTONUP, JOYHATMOTION
            
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            for event in pygame.event.get(): # User did something.
                if event.type == pygame.QUIT: # If user clicked close.
                   self.done = True # Flag that we are done so we exit this loop.
                elif event.type == pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")
                    if joystick.get_button(0) == 1:
                        print("Désactivation du PA")
                        self.window.onButtonPushSignal(True)
                elif event.type == pygame.JOYBUTTONUP:
                    print("Joystick button released.")

            screen.fill(WHITE)
            textPrint.reset()


            # Get the name from the OS for the controller/joystick.
            name = joystick.get_name()
            textPrint.tprint(screen, "Joystick name: {}".format(name))


            # Usually axis run in pairs, up/down for one, and left/right for
            # the other.
            axes = joystick.get_numaxes()
            textPrint.tprint(screen, "Number of axes: {}".format(axes))
            textPrint.indent()

            if ((abs(self.window.pBrut) < 0.5) and (abs(joystick.get_axis(0)) > 0.5)) or ((abs(self.window.nzBrut) < 0.5) and (abs(joystick.get_axis(1)) > 0.5)):
                print("Désactivation du PA")
                self.window.onButtonPushSignal(True)

            self.window.pBrut = joystick.get_axis(0)
            textPrint.tprint(screen, "Axis 0 value: {:>6.3f}".format(joystick.get_axis(0)))
            self.window.nzBrut = joystick.get_axis(1)
            textPrint.tprint(screen, "Axis 1 value: {:>6.3f}".format(joystick.get_axis(1)))

            

            textPrint.unindent()

            buttons = joystick.get_numbuttons()
            textPrint.tprint(screen, "Number of buttons: {}".format(buttons))
            textPrint.indent()

            for i in range(buttons):
                button = joystick.get_button(i)
                textPrint.tprint(screen,"Button {:>2} value: {}".format(i, button))
            textPrint.unindent()
            textPrint.unindent()

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # Limit to 20 frames per second.
            clock.tick(20)

        pygame.quit()




