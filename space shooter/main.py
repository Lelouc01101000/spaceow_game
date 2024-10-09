import pygame
from random import randint, uniform
import time



pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 630
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("spaceow")
running = True
clock = pygame.time.Clock()
meteors_destroyed = 0




class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)  # group argument is needed cause we want to group object player with other sprites in vairbale all_sprites

        self.image = player_surf#pygame.image.load('images/shimeji.png').convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 300

        # cooldown for laser shot
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # mask, defining it is not neccassery as pygame will provide one automatically when calling method we need it for, but it might be useful for somethign else in future
        self.mask = pygame.mask.from_surface(self.image)




    def laser_timer(self):  # this will get called all the time, cause its in update
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()  # current_time will increase every moment and be dynamical vairable which's value will keep increasing

            # if cooldown_duration passed, therefore if current_time's value has increased by cooldown_duration ammount since last laser was shot, then this will execute
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        '''
        if right key is pressed it gives value True which is then converted to integer and becomes one, if its not pressed then value given is false and gets converted to 0
        if left key is pressed it gives value True which is then converted to integet and becomes one, assuming right key isnt pressed it will be 0-1 or moving to negative x direction therefore left
        if both left and right is pressed we will get 1-1 which is zero
        same logic applies to up and down, for going down we increase y value by 1 and for going up we decrease it
        '''
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        '''
        when going diagonallys speed will become combination of x and y, even though diagonal movement speed should be less then both
        to avoid this we normalize direction vector
        vector will return false if its value is 0, thats why we can use it in if statement as such
        '''
        self.direction = self.direction.normalize() if self.direction else self.direction

        # center of players photo moves by direction times speed times dr which syncs it for diferent fps we can combine speed and direction but that will make altering values more of a chore
        self.rect.center += self.direction * self.speed * dt

        '''---------------------  MANAGING WHEN LASER IS SHOT AND ETC  ---------------------'''
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:  # statement will be called when self.can_shoot is true
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            # laser_shoot_time will store value of time when laser was shot, it wont increase every moment unlike current_time cause this if statement is called once and then becomes false while current_time's if statement gets called continuesly before it becomes false, so time for current_time increases dynamically
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):  # (needed variable self, surf stands for surface, pos stands for position, groups connects it with otehr classes)
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)
        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf # we are creating original_surf because it is one that will be manipulated while rotating, more about it in def update
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        #self.lifetime = 3000
        self.speed = randint(400, 650)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)  # x direction can be diagonal anywhere from -0.5 to 0.5 and y direction is 1
        # mask
        self.mask = pygame.mask.from_surface(self.image)

        # transformation
        self.rotation = 0 #rotation angle which will be incremented based on how fast we want object to rotate
        self.rotation_speed = randint(20,50) # speed of rotation being random



    def update(self, dt):
        self.rect.centerx += self.direction.x * self.speed * dt
        self.rect.centery += self.direction.y * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

        # rotation will rotate original picture from its original position
        # instead of rotating object by some magnitude and rotating new object that has been rotated by some magnitude again
        # it just goes back to original image and rotates it by bigger magnitude
        # this is why we needed to define original_surface and use it alongside self.image
        # we multiply it by dt to sync it with frame rate
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center) # self.rect should have same value as new rotated meteor so hitboxes are consistent with displayed image


class AnimatedExplosions(pygame.sprite.Sprite):
    def __init__(self,frames,pos,groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    def update(self,dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames): # we dont want this to run more than ammount of pictures we have and therefore ammount of elements in self.frames
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()




def collisions():
    global running # without this we cant effect globally present running variable from function
    # pygame.sprite.collide_mask makes sure collision is depended on visible pixels only and not invisible pixels that surround drawing of ship for example
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask) # if player and meteor collide nothing will happen besides collision being reocrded
    if collision_sprites:
        running = False # if collision_sprites is met than game ends


    for laser in laser_sprites: # iterating through infinite list of laser sprites, because we only want to effect one thats present and not all the lasers that might be shot
        collided_sprites  = pygame.sprite.spritecollide(laser, meteor_sprites, True) # if laser collides with meteor then meteor sprite is deleted
        if collided_sprites:
            laser.kill() # if laser collided with meteor its destroyed, this is to avoid laser going through many meteors and destroying whole row of them
                         # additionally it destroys object which is needed for better game performance as otherwise sprite will exist till the game is over
            AnimatedExplosions(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            global meteors_destroyed
            meteors_destroyed += 1


def display_score():
    global current_time
    # font.render takes string as value which it displays so we cast current_time as string, first it is casted as int cause it has floating value which looks ugly when displayed
    # boolean value in font.render indicates if we want to smooth out edges of text or not
    # meteors_destroyed * 50 so each meteor grants 50 points
    text_surf = font.render(str(int(current_time + meteors_destroyed*50)), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)

    # draws rectangle on display_surface, with rgb(240,240,240), adds rectangle over the text_rect string, it wraps around text on it own without any parameters
    # its inflated (20,10) to have rounder edges
    # it is moved on x by 0 and on y by -8 cause this method is used for letters which sometimes go down and need bigger vertical box, unlike text_rect which displays score via numbers
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-5),5,10)


def game_over():

    #display_surface.fill((0,0,0))
    display_surface.blit(game_over_background_surf, (0, 0))
    global font
    global running
    global current_time

    game_over_text = font.render("GAME OVER",True, (200,200,200))
    screen_text = font.render(f"Your score was:  {int(current_time + meteors_destroyed*50)}", False, (200, 200, 200))
    time_text = font.render(f"You survived for:  {int(current_time/10)} seconds", True, (200,200,200))
    display_surface.blit(game_over_text, (WINDOW_WIDTH/2 - (game_over_text.get_width()/2), (WINDOW_HEIGHT/2 - 50)))
    display_surface.blit(screen_text, (WINDOW_WIDTH/2 - (screen_text.get_width()/2), (WINDOW_HEIGHT/2) ))
    display_surface.blit(time_text, (WINDOW_WIDTH/2 -(time_text.get_width()/2), (WINDOW_HEIGHT/2 + 50) ))

    for character in all_sprites:
        character.kill()
    pygame.display.update()
    time.sleep(10)

    print("Game over")
    print(current_time + meteors_destroyed * 50)
    current_time = 0
    pygame.quit()




# importing images
background_surf = pygame.image.load('images/background1.jpg').convert_alpha()

game_over_background_surf = pygame.image.load('images/background.jpg').convert_alpha()

player_surf = pygame.image.load('images/shimeji.png').convert_alpha()

meteor_surf = pygame.transform.smoothscale(pygame.image.load('images/egg_one.png').convert_alpha(), (150,105)) #original size is 1500 by 1050

laser_surf = pygame.image.load('images/fish1.png').convert_alpha()

font = pygame.font.Font("images/Oxanium-Bold.ttf", 20)

explosion_frames = [pygame.image.load(f"images/explosion/{i}.png").convert_alpha() for i in range(21)]
laser_sound =  pygame.mixer.Sound("audio/mewo.mp3")
#laser_sound.set_volume(0.5) # makes laser half as loud
explosion_sound = pygame.mixer.Sound("audio/eggsplotion.mp3")
explosion_sound.set_volume(0.4)

damage_sound = pygame.mixer.Sound("audio/damage.ogg") # this one is not used cause game ends when collison happens

game_music = pygame.mixer.Sound = pygame.mixer.Sound("audio/gamesong1.mp3")
game_music.set_volume(0.1)
game_music.play(loops = -1)  # makes sure game plays infinitely



# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
player = Player(all_sprites)



# meteor event timer
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 400)  # creates meteor every 0.45 second




while running:
    dt = clock.tick() / 1000  # needed to manage fps on different devices, so players can have higher fps if better device without moving faster cause of it
    current_time = pygame.time.get_ticks() / 100  # using at as score value but milliseconds increase too fast so divided by 100, this gives 10 points per sec

    '''---------- EVENT LOOP ----------'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    all_sprites.update(dt)

    collisions()

    display_score()

    all_sprites.draw(display_surface) # displays sprites form all_sprites list variable


    pygame.display.update()

    display_surface.blit(background_surf, (0, 0))


game_over()
