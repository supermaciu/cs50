--[[
    GD50
    Breakout Remake

    -- PlayState Class --

    Author: Colton Ogden
    cogden@cs50.harvard.edu

    Represents the state of the game in which we are actively playing;
    player should control the paddle, with the ball actively bouncing between
    the bricks, walls, and the paddle. If the ball goes below the paddle, then
    the player should lose one point of health and be taken either to the Game
    Over screen if at 0 health or the Serve screen otherwise.
]]

PlayState = Class{__includes = BaseState}

POWERUP_SPAWN_HIT_THRESHOLD = 20
POWERUP_SPAWN_TIME = 10 -- made to fix softlock when there is only locked bricks

--[[
    We initialize what's in our PlayState via a state table that we pass between
    states as we go from playing to serving.
]]
function PlayState:enter(params)
    self.paddle = params.paddle
    self.bricks = params.bricks
    self.health = params.health
    self.score = params.score
    self.highScores = params.highScores
    self.balls = params.balls
    self.level = params.level
    self.recoverPoints = params.recoverPoints

    self.powerupsCollected = params.powerupsCollected

    -- give ball random starting velocity
    for i, ball in pairs(self.balls) do
        ball.dx = math.random(-200, 200)
        ball.dy = math.random(-50, -60)
    end

    self.powerupsFalling = {}
    self.brickHits = 0
    self.powerupTimer = 0
end

function PlayState:update(dt)
    self.powerupTimer = self.powerupTimer + dt
    if self.powerupTimer >= POWERUP_SPAWN_TIME then
        self:spawnPowerup()
        self.powerupTimer = 0
    end

    if self.paused then
        if love.keyboard.wasPressed('space') then
            self.paused = false
            gSounds['pause']:play()
        else
            return
        end
    elseif love.keyboard.wasPressed('space') then
        self.paused = true
        gSounds['pause']:play()
        return
    end

    -- update positions based on velocity
    self.paddle:update(dt)
    for i, ball in pairs(self.balls) do
        ball:update(dt)
    end

    -- update powerupsFalling
    for i, powerup in pairs(self.powerupsFalling) do
        powerup:update(dt)
    end

    for i, ball in pairs(self.balls) do
        if ball:collides(self.paddle) then
            -- raise ball above paddle in case it goes below it, then reverse dy
            ball.y = self.paddle.y - 8
            ball.dy = -ball.dy
    
            --
            -- tweak angle of bounce based on where it hits the paddle
            --
    
            -- if we hit the paddle on its left side while moving left...
            if ball.x < self.paddle.x + (self.paddle.width / 2) and self.paddle.dx < 0 then
                ball.dx = -50 + -(8 * (self.paddle.x + self.paddle.width / 2 - ball.x))
            
            -- else if we hit the paddle on its right side while moving right...
            elseif ball.x > self.paddle.x + (self.paddle.width / 2) and self.paddle.dx > 0 then
                ball.dx = 50 + (8 * math.abs(self.paddle.x + self.paddle.width / 2 - ball.x))
            end
    
            gSounds['paddle-hit']:play()
        end
    end

    -- detect collision across all bricks with the ball
    for k, brick in pairs(self.bricks) do
        for i, ball in pairs(self.balls) do
            -- only check collision if we're in play
            if brick.inPlay and ball:collides(brick) then

                if brick.locked and self:countKeyPowerupsCollected() > 0 then
                    self.score = self.score + 1000
                    table.remove(self.powerupsCollected, table.find(self.powerupsCollected, 10))
                    brick:hit()
                elseif not brick.locked then
                    self.score = self.score + (brick.tier * 200 + brick.color * 25)
                    brick:hit()
                end

                -- if we have enough points, recover a point of health
                if self.score >= self.recoverPoints and (self.paddle.size < 4 or self.health < 3) then
                    -- can't go above 3 health
                    self.health = math.min(3, self.health + 1)

                    -- multiply recover points by 2
                    self.recoverPoints = math.min(100000, self.recoverPoints * 2)

                    -- play recover sound effect
                    gSounds['recover']:play()

                    -- upgrade size
                    self.paddle:changeSize(math.min(4, self.paddle.size+1))
                end

                -- go to our victory screen if there are no more bricks left
                if self:checkVictory() then
                    gSounds['victory']:play()

                    gStateMachine:change('victory', {
                        level = self.level,
                        paddle = self.paddle,
                        health = self.health,
                        score = self.score,
                        highScores = self.highScores,
                        ball = ball,
                        recoverPoints = self.recoverPoints
                    })
                end

                --
                -- collision code for bricks
                --
                -- we check to see if the opposite side of our velocity is outside of the brick;
                -- if it is, we trigger a collision on that side. else we're within the X + width of
                -- the brick and should check to see if the top or bottom edge is outside of the brick,
                -- colliding on the top or bottom accordingly 
                --

                -- left edge; only check if we're moving right, and offset the check by a couple of pixels
                -- so that flush corner hits register as Y flips, not X flips
                if ball.x + 2 < brick.x and ball.dx > 0 then
                    
                    -- flip x velocity and reset position outside of brick
                    ball.dx = -ball.dx
                    ball.x = brick.x - 8
                
                -- right edge; only check if we're moving left, , and offset the check by a couple of pixels
                -- so that flush corner hits register as Y flips, not X flips
                elseif ball.x + 6 > brick.x + brick.width and ball.dx < 0 then
                    
                    -- flip x velocity and reset position outside of brick
                    ball.dx = -ball.dx
                    ball.x = brick.x + 32
                
                -- top edge if no X collisions, always check
                elseif ball.y < brick.y then
                    
                    -- flip y velocity and reset position outside of brick
                    ball.dy = -ball.dy
                    ball.y = brick.y - 8
                
                -- bottom edge if no X collisions or top collision, last possibility
                else
                    
                    -- flip y velocity and reset position outside of brick
                    ball.dy = -ball.dy
                    ball.y = brick.y + 16
                end

                -- slightly scale the y velocity to speed up the game, capping at +- 150
                if math.abs(ball.dy) < 150 then
                    ball.dy = ball.dy * 1.02
                end

                -- spawn a powerup if hit enough times
                self.brickHits = brick.locked and self.brickHits or self.brickHits + 1
                if self.brickHits >= POWERUP_SPAWN_HIT_THRESHOLD then
                    self:spawnPowerup()
                end

                -- only allow colliding with one brick, for corners
                break
            end
        end
    end

    local ballsToRemove = {}
    for i, ball in pairs(self.balls) do
        -- if ball goes below bounds, revert to serve state and decrease health
        if ball.y >= VIRTUAL_HEIGHT then
            if #self.balls > 1 then
                table.insert(ballsToRemove, ball)
            else
                self.health = self.health - 1
                gSounds['hurt']:play()
    
                if self.health == 0 then
                    gStateMachine:change('game-over', {
                        score = self.score,
                        highScores = self.highScores
                    })
                else
                    gStateMachine:change('serve', {
                        paddle = self.paddle,
                        bricks = self.bricks,
                        health = self.health,
                        score = self.score,
                        highScores = self.highScores,
                        level = self.level,
                        recoverPoints = self.recoverPoints,
                        powerupsCollected = self.powerupsCollected
                    })
                end

                -- decrease paddle size
                self.paddle:changeSize(math.max(1, self.paddle.size-1))
            end
        end
    end

    for i, ball in pairs(ballsToRemove) do
        table.remove(self.balls, table.find(self.balls, ball))
    end

    local powerupsFallingToRemove = {}
    for i, powerupFalling in pairs(self.powerupsFalling) do
        if powerupFalling:collides(self.paddle) then
            if powerupFalling.powerupType == 9 then
                -- more balls powerup
                for i=1, 2 do
                    local newBall = Ball(math.random(7))
                    newBall:reset()
                    newBall.dx = math.random(-200, 200)
                    newBall.dy = math.random(-50, -60)
                    table.insert(self.balls, newBall)
                end
            elseif powerupFalling.powerupType == 10 then
                -- key for locked brick
                table.insert(self.powerupsCollected, 10)
            end

            table.insert(powerupsFallingToRemove, powerupFalling)
            gSounds['score']:play()
        end
    end

    for i, powerupFalling in pairs(powerupsFallingToRemove) do
        table.remove(self.powerupsFalling, table.find(self.powerupsFalling, powerupFalling))
    end

    -- for rendering particle systems
    for k, brick in pairs(self.bricks) do
        brick:update(dt)
    end

    if love.keyboard.wasPressed('escape') then
        love.event.quit()
    end
end

function PlayState:render()
    -- render bricks
    for k, brick in pairs(self.bricks) do
        brick:render()
    end

    -- render all particle systems
    for k, brick in pairs(self.bricks) do
        brick:renderParticles()
    end

    self.paddle:render()
    for i, ball in pairs(self.balls) do
        ball:render()
    end

    -- update powerupsFalling
    for i, powerupFalling in pairs(self.powerupsFalling) do
        powerupFalling:render()
    end

    renderScore(self.score)
    renderHealth(self.health)
    renderPowerupsCollected(self.powerupsCollected)

    -- pause text, if paused
    if self.paused then
        love.graphics.setFont(gFonts['large'])
        love.graphics.printf("PAUSED", 0, VIRTUAL_HEIGHT / 2 - 16, VIRTUAL_WIDTH, 'center')
    end
end

function PlayState:checkVictory()
    for k, brick in pairs(self.bricks) do
        if brick.inPlay then
            return false
        end 
    end

    return true
end

function PlayState:countLockedBricks()
    local count = 0

    for k, brick in pairs(self.bricks) do
        if brick.inPlay and brick.locked then
            count = count + 1
        end 
    end

    return count
end

function PlayState:countKeyPowerupsCollected()
    local count = 0

    for i, powerupCollected in pairs(self.powerupsCollected) do
        if powerupCollected == 10 then
            count = count + 1
        end
    end

    return count
end

function PlayState:countKeyPowerupsFalling()
    local count = 0

    for i, powerupFalling in pairs(self.powerupsFalling) do
        if powerupFalling.powerupType == 10 then
            count = count + 1
        end
    end

    return count
end

function PlayState:spawnPowerup()
    local powerUpOptions = {9}

    if self:countKeyPowerupsCollected() < self:countLockedBricks() and self:countKeyPowerupsFalling() < self:countLockedBricks() then
        table.insert(powerUpOptions, 10)
    end

    table.insert(self.powerupsFalling, Powerup(powerUpOptions[math.random(1, #powerUpOptions)]))
    self.brickHits = 0
end