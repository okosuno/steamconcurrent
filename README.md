# steamconcurrent

<p align="center">
<img src="https://imgur.com/LQW9fp0.png"/>
</br>polybar display</br></br>
<img src="https://i.imgur.com/kf8Bfip.png"/>  
</br>terminal display</br></br>
<img src="https://imgur.com/pACwQDO.png"/>
</br>list view</br></br> 
<img src="https://i.imgur.com/PGujgpc.png"/>
</br>config prompt</br></br>
</p>

### what it does
tracks multiple steam games for the number of concurrent players online right now for display in terminal or polybar.  
also displays how far the current player count varies from the average.  
search for, add, and remove games via title or appid.  
takes some configuration options such as query and refresh interval.  
uses default terminal palette in display (looks good with pywal etc.)

### how it does it
this program only queries the steam web api, it doesn't scrape steamdb or any other third-party sites.  
it fetches a list of every steam game and appid and builds a queriable sqlite db.  
this lets players search for games or quickly add games they know the exact name of without running to search for appids.  
it then builds a tracking db for each game added.  
it will track and store these numbers at user-defined intervals with sensible defaults to keep cpu & storage footprint low.  

### limitations
display modes show variance from average using the historical data tracked only since the game was added to the local db.  
the local database of steam games is currently about 8MB, pretty heavy.  
between that and having the user grab 8MB of data from steam every time they search for a game, i opted for local cacheing.  

### why did you do it like that
steams api does not track historical player count data for its games.   
websites like steamdb.info explicitly disallow querying it for data.   
keeping a local database of player count data is currently the only solution i can find to produce the kind of output i want.  

### future plans
1. users can choose default periods for averages (1 day, 1 week, 1 month, all time) in polybar/simple view.  
2. more fun stats. (e.g. peak player count, best days to play, best time of day to play, etc)  
3. creating an advanced view which displays in terminal like "simple" display but cycles through games like polybar, only with more display options.  
4. windows-compatible GUI _or_ windows mode with windows notifications.  

### lessons learned
1. it is a good idea to set up unit testing as you're building the program.  
2. definitely set up debugging from the beginning as well.  
3. sqlite can be ornery if you don't properly handle the opening and close of connections. in the future i would ensure my structure allows me to open and close the db connection far less often than this program does.  
4. even though there is no concurrency left in the program, i did explore that as an avenue for querying the database in consistent intervals. i learned a lot about passing data between threads and why it should be avoided.  
5. scope creep can be devastating for side projects. write the plan first, deviate as little as possible. multiple reformats makes you wish you just did a rewrite.  
6. circular imports are nasty.  
7. data serialization is handy.  
8. i have a very, very lot to learn.  

### how do it use it

`git clone https://github.com/okosuno/steamconcurrent.git`  
`cd steamconcurrent`  
`pip install -r requirements.txt`  
`python main_temp.py --help`  

1. you'll likely want to run `--setup` first
2. and then start adding games with `--name [query]`
3. or searching for games with `--query --name [query]`
4. check the games you've added with `--list`

after it's set up you can just run whichever mode you want: `-d` or `-p`
