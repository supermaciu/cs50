--[[
    ScoreState Class
    Author: Colton Ogden
    cogden@cs50.harvard.edu

    A simple state used to display the player's score before they
    transition back into the play state. Transitioned to from the
    PlayState when they collide with a Pipe.
]]

ScoreState = Class{__includes = BaseState}

BRONZE_THRESHOLD = 2
SILVER_THRESHOLD = 5
GOLD_THRESHOLD = 7

MEDALS = {
    [1] = love.graphics.newImage("bronze.png"),
    [2] = love.graphics.newImage("silver.png"),
    [3] = love.graphics.newImage("gold.png")
}

function ScoreState:init()
    self.medal = 0
end

function ScoreState:enter(params)
    self.score = params.score

    if self.score >= BRONZE_THRESHOLD then self.medal = 1 end
    if self.score >= SILVER_THRESHOLD then self.medal = 2 end
    if self.score >= GOLD_THRESHOLD then self.medal = 3 end
end

function ScoreState:update(dt)
    -- go back to play if enter is pressed
    if love.keyboard.wasPressed('enter') or love.keyboard.wasPressed('return') then
        gStateMachine:change('countdown')
    end
end

function ScoreState:render()
    -- simply render the score to the middle of the screen
    love.graphics.setFont(flappyFont)
    love.graphics.printf('Oof! You lost!', 0, 64, VIRTUAL_WIDTH, 'center')

    love.graphics.setFont(mediumFont)
    love.graphics.printf('Score: ' .. tostring(self.score), 0, 100, VIRTUAL_WIDTH, 'center')

    for i = 1, self.medal do
        love.graphics.draw(MEDALS[i], VIRTUAL_WIDTH/2-26+18*(i-1), 120)
    end

    love.graphics.printf('Press Enter to Play Again!', 0, 160, VIRTUAL_WIDTH, 'center')
end