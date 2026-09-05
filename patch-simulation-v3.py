from pathlib import Path
p=Path('lib/simulation.ts');s=p.read_text()
start=s.index('export const WEAPONS');end=s.index('export type Input')
s=s[:start]+'''import { WEAPONS, SELECTABLE, allowedWeapon, allowedGrenades, startingInventory, weaponMuzzle, MUZZLE_FLASH_DURATION, DEFAULT_RULES, validRules, type MatchRules } from './weapons';
import { createBotMemory, perceive, type BotMemory } from './perception';
import { ROOM_PROTOCOL } from './room-discovery';
export { WEAPONS, SELECTABLE } from './weapons';
'''+s[end:]
s=s.replace('grenade:boolean;weapon:number','grenade:boolean;pickup:boolean;weapon:number').replace('grenade:false,weapon:-1','grenade:false,pickup:false,weapon:-1')
s=s.replace('weapon:number;ammo:number[]','weapon:number;preferredWeapon:number;inventory:(number|null)[];ammo:number[]')
s=s.replace('lastHit:number;killer:string','lastHit:number;lastHitFrom:Vec|null;killer:string')
s=s.replace("type:'shot'|'hit'|'death'|'explosion'|'patch'|'limb'", "type:'shot'|'hit'|'bleed'|'death'|'explosion'|'patch'|'limb'|'pickup'")
s=s.replace('export type State = {map:', "export type Pickup={id:number;weapon:number;pos:Vec;cooldown:number;dropped:boolean;expires:number};\nexport type State = {protocol:number;rules:MatchRules;pickups:Pickup[];map:")
s=s.replace("'patch','grenade'] as const", "'patch','grenade','pickup'] as const")
s=s.replace('aiPaths=new Map', 'brains=new Map<string,BotMemory>();aiPaths=new Map')
s=s.replace('constructor(map:MapId,random:()=>number=Math.random)', 'constructor(map:MapId,random:()=>number=Math.random,rules:MatchRules=DEFAULT_RULES)')
s=s.replace("this.state={map,time:0", "this.state={protocol:ROOM_PROTOCOL,rules:{...(validRules(rules)?rules:DEFAULT_RULES)},pickups:[],map,time:0")
s=s.replace("events:[],winner:-1};\n  }", "events:[],winner:-1};this.createPickups();\n  }")
s=s.replace('weapon,ammo:WEAPONS.map', 'weapon,preferredWeapon:weapon,inventory:startingInventory(this.state.rules,weapon),ammo:WEAPONS.map')
s=s.replace('lastHit:-10,killer:', 'lastHit:-10,lastHitFrom:null,killer:')
s=s.replace('this.inputs.delete(id);}', 'this.inputs.delete(id);this.brains.delete(id);this.aiPaths.delete(id);}')
s=s.replace("a.limbs=[true,true,true,true];a.ammo=", "a.limbs=[true,true,true,true];a.inventory=startingInventory(this.state.rules,a.preferredWeapon);a.weapon=a.inventory.includes(a.preferredWeapon)?a.preferredWeapon:a.inventory.find((id):id is number=>id!==null)!;a.lastHit=-10;a.lastHitFrom=null;a.firing=0;this.brains.delete(a.id);this.aiPaths.delete(a.id);a.ammo=")
s=s.replace('a.kits=1;a.grenades=3;', 'a.kits=1;a.grenades=allowedGrenades(this.state.rules)?3:0;')
s=s.replace('s.remaining=Math.max(0,s.remaining-dt);', "s.remaining=Math.max(0,s.remaining-dt);\n    for(const p of s.pickups)p.cooldown=Math.max(0,p.cooldown-dt);s.pickups=s.pickups.filter(p=>!p.dropped||p.expires>s.time);")
s=s.replace("this.event('hit',v(a.pos.x,a.pos.y+.7", "this.event('bleed',v(a.pos.x,a.pos.y+.7")
s=s.replace('this.act(a,input,dt);', "this.act(a,input,dt);if(!a.bot)for(const key of ['use','turret','patch','grenade','jump','reload','pickup'] as const)input[key]=false;")
start=s.index('    for(const p of [...s.projectiles])');end=s.index('    if(s.remaining===0',start)
s=s[:start]+'''    for(const p of [...s.projectiles]){
      const old={...p.pos},speed=Math.hypot(p.vel.x,p.vel.y,p.vel.z),len=speed*dt;if(len<=0)continue;
      const d=v(p.vel.x/speed,p.vel.y/speed,p.vel.z/speed);let hit=wallDistance(this.world,old,d),direct='';const owner=s.actors.find(a=>a.id===p.owner);
      for(const a of s.actors)if(a.id!==p.owner&&a.dead<=0&&a.team!==owner?.team){const t=rayBox(old,d,v(a.pos.x-.45,a.pos.y,a.pos.z-.45),v(a.pos.x+.45,a.pos.y+2,a.pos.z+.45));if(t<hit){hit=t;direct=a.id;}}
      for(const c of s.vehicles)if(!c.dead&&owner?.vehicle!==c.id){const t=rayBox(old,d,v(c.pos.x-1.25,0,c.pos.z-2.1),v(c.pos.x+1.25,2.1,c.pos.z+2.1));if(t<hit){hit=t;direct='';}}
      p.pos.x+=p.vel.x*dt;p.pos.y+=p.vel.y*dt;p.pos.z+=p.vel.z*dt;if(p.grenade)p.vel.y-=9*dt;p.life-=dt;
      if(hit<=len||p.pos.y<.1||p.life<=0||Math.abs(p.pos.x)>36||Math.abs(p.pos.z)>36){
        if(hit<=len)p.pos=v(old.x+d.x*hit,old.y+d.y*hit,old.z+d.z*hit);else direct='';
        this.explode(p.pos,p.owner,p.grenade?85:140,p.grenade?4:6,p.grenade?'':direct,p.grenade?0:2);
        s.projectiles=s.projectiles.filter(q=>q.id!==p.id);
      }
    }
'''+s[end:]
s=s.replace('a.yaw=i.yaw;a.pitch=i.pitch;', 'a.yaw=i.yaw;a.pitch=i.pitch;')
s=s.replace("if(i.weapon>=0&&i.weapon!==a.weapon&&!a.vehicle)", "if(i.pickup&&!a.vehicle)this.pickup(a);\n    if(i.weapon>=0&&i.weapon!==a.weapon&&!a.vehicle&&a.inventory.includes(i.weapon)&&allowedWeapon(i.weapon,this.state.rules))")
s=s.replace('if(i.grenade&&a.weapon===1', 'if(i.grenade&&allowedGrenades(this.state.rules)&&a.weapon===1')
start=s.index('  fire(a:Actor)');end=s.index('  damage(a:Actor',start)
s=s[:start]+'''  trace(a:Actor,o:Vec,d:Vec){
    let dist=wallDistance(this.world,o,d),target:Actor|undefined,part=-1,car:Vehicle|undefined;
    for(const c of this.state.vehicles)if(!c.dead&&c.id!==a.vehicle){const t=rayBox(o,d,v(c.pos.x-1.15,0,c.pos.z-2.15),v(c.pos.x+1.15,2.1,c.pos.z+2.15));if(t<dist){dist=t;car=c;}}
    for(const other of this.state.actors){if(other.id===a.id||other.dead>0||other.team===a.team||other.seat==='driver')continue;
      const p=other.pos,low=!other.limbs[2]&&!other.limbs[3]?.6:0;
      const pieces=[[-.24,1.47-low,-.24,.24,1.98-low,.24,-2],[-.34,.76-low,-.24,.34,1.46-low,.24,-1],[-.60,.81-low,-.24,-.34,1.42-low,.24,0],[.34,.81-low,-.24,.60,1.42-low,.24,1],[-.34,0,-.24,-.02,.75,.24,2],[.02,0,-.24,.34,.75,.24,3]];
      for(const [x,y,z,X,Y,Z,partId] of pieces){if(partId>=0&&!other.limbs[partId])continue;const hit=rayBox(o,d,v(p.x+x,p.y+y,p.z+z),v(p.x+X,p.y+Y,p.z+Z));if(hit<dist){dist=hit;target=other;part=partId;car=undefined;}}
    }
    return {dist,target,part,car,end:v(o.x+d.x*dist,o.y+d.y*dist,o.z+d.z*dist)};
  }
  muzzle(a:Actor){return weaponMuzzle(a,this.state.vehicles.find(c=>c.id===a.vehicle)?.yaw||0);}
  fire(a:Actor){
    const wi=a.seat==='turret'?3:a.weapon,w=WEAPONS[wi];
    if(!w||!allowedWeapon(wi,this.state.rules)||(a.seat!=='turret'&&!a.inventory.includes(wi))||a.seat==='driver'||a.dead>0||a.cooldown>0||a.reload>0)return;
    if(a.ammo[wi]<=0){this.reload(a);return;}a.ammo[wi]--;a.cooldown=w.interval;a.firing=MUZZLE_FLASH_DURATION;a.protect=0;
    if(w.rocket){this.launch(a,false);return;}
    const spread=w.spread*(a.ads?.3:1)*(a.bot?2:1)*(a.limbs[0]&&a.limbs[1]?1:2.2);
    const aim=lookDirection(a.yaw+(this.random()-.5)*spread,a.pitch+(this.random()-.5)*spread),eyes=eye(a),aimHit=this.trace(a,eyes,aim);
    let origin=this.muzzle(a);const toMuzzle=distance(eyes,origin),safe=v((origin.x-eyes.x)/toMuzzle,(origin.y-eyes.y)/toMuzzle,(origin.z-eyes.z)/toMuzzle);
    const obstruction=wallDistance(this.world,eyes,safe);
    if(obstruction<toMuzzle){this.event('shot',origin,a.id,{end:v(eyes.x+safe.x*obstruction,eyes.y+safe.y*obstruction,eyes.z+safe.z*obstruction),weapon:wi});return;}
    const dist=distance(origin,aimHit.end),d=v((aimHit.end.x-origin.x)/dist,(aimHit.end.y-origin.y)/dist,(aimHit.end.z-origin.z)/dist),hit=this.trace(a,origin,d);
    this.event('shot',origin,a.id,{end:hit.end,weapon:wi});
    if(hit.target)this.damage(hit.target,w.damage*(hit.part===-2?w.headshot:hit.part>=0?.85:1),a.id,hit.part);
    if(hit.car)this.damageVehicle(hit.car,w.damage*.4,a.id);
  }
  launch(a:Actor,grenade:boolean){
    const aim=lookDirection(a.yaw,a.pitch),eyes=eye(a),target=this.trace(a,eyes,aim).end,o=this.muzzle(a),distanceToAim=distance(o,target);
    const d=v((target.x-o.x)/distanceToAim,(target.y-o.y)/distanceToAim,(target.z-o.z)/distanceToAim);
    a.firing=MUZZLE_FLASH_DURATION;a.protect=0;this.event('shot',o,a.id,{weapon:a.weapon});
    const between=distance(eyes,o),toward=v((o.x-eyes.x)/between,(o.y-eyes.y)/between,(o.z-eyes.z)/between),obstruction=wallDistance(this.world,eyes,toward);
    if(obstruction<between){this.explode(v(eyes.x+toward.x*obstruction,eyes.y+toward.y*obstruction,eyes.z+toward.z*obstruction),a.id,grenade?85:140,grenade?4:6,'',grenade?0:2);return;}
    this.state.projectiles.push({id:++this.seq,owner:a.id,pos:{...o},vel:v(d.x*(grenade?22:33),d.y*(grenade?22:33)+(grenade?2:0),d.z*(grenade?22:33)),life:grenade?2.5:4,grenade});
  }
'''+s[end:]
s=s.replace('part=-1,explosive=false){','part=-1,explosive=false,from?:Vec){')
s=s.replace('a.lastHit=this.state.time;a.killer=', 'a.lastHit=this.state.time;a.lastHitFrom=from?{...from}:source?{...source.pos}:null;a.killer=')
s=s.replace('Math.min(4,a.bleed+amount*.018)', 'Math.min(2.5,a.bleed+amount*.009)').replace('Math.min(4,a.bleed+1)', 'Math.min(2.5,a.bleed+.6)')
s=s.replace('a.hp=0;a.dead=5;', 'a.hp=0;this.dropWeapon(a.weapon,a.pos,a.ammo[a.weapon]);a.dead=5;')
start=s.index('  explode(p:Vec');end=s.index('  damageVehicle(',start)
s=s[:start]+'''  explode(p:Vec,owner:string,damage:number,radius:number,directId='',lethalRadius=0){this.event('explosion',p,owner);
    for(const a of this.state.actors){
      if(a.dead>0)continue;
      if(a.id===directId){this.damage(a,220,owner,-1,true,p);continue;}
      const q=v(a.pos.x,a.pos.y+1,a.pos.z),dist=distance(p,q);if(dist>radius)continue;
      if(dist>.001){const dir=v((q.x-p.x)/dist,(q.y-p.y)/dist,(q.z-p.z)/dist);if(wallDistance(this.world,v(p.x+dir.x*.03,p.y+dir.y*.03,p.z+dir.z*.03),dir)<dist-.15)continue;}
      const amount=dist<=lethalRadius?damage:damage*(1-(dist-lethalRadius)/(radius-lethalRadius));
      this.damage(a,amount,owner,Math.floor(this.random()*4),true,p);
    }
    for(const car of this.state.vehicles)if(!car.dead&&distance(car.pos,p)<radius+2)this.damageVehicle(car,damage*2*(1-Math.max(0,distance(car.pos,p)-2)/radius),owner);
  }
'''+s[end:]
s=s.replace("mount(a:Actor,seat:string){if(a.dead>0)return;", "mount(a:Actor,seat:string){if(a.dead>0||(seat==='turret'&&!allowedWeapon(3,this.state.rules)))return;")
start=s.index('  ai(a:Actor');end=s.index('  path(start:Vec',start)
s=s[:start]+'''  createPickups(){
    const pads:[[number,number],number][]=[[[ -4,25],2],[[4,-25],2],[[-15,12],7],[[15,-12],8],[[-15,-17],4],[[15,17],5],[[-4,30],9],[[4,-30],6],[[0,20],1],[[0,-14],0]];
    this.state.pickups=pads.filter(([,weapon])=>allowedWeapon(weapon,this.state.rules)).map(([[x,z],weapon])=>({id:++this.seq,weapon,pos:v(x,0,z),cooldown:0,dropped:false,expires:Infinity}));
    // JSON transport must not carry Infinity.
    for(const p of this.state.pickups)p.expires=0;
  }
  nearestPickup(a:Actor):Pickup|undefined{
    return this.state.pickups.filter(p=>p.cooldown===0&&allowedWeapon(p.weapon,this.state.rules)&&distance(a.pos,p.pos)<2.1).filter(p=>{
      const origin=eye(a),end=v(p.pos.x,.65,p.pos.z),dist=distance(origin,end),dir=v((end.x-origin.x)/dist,(end.y-origin.y)/dist,(end.z-origin.z)/dist);return wallDistance(this.world,origin,dir)>=dist-.05;
    }).sort((p,q)=>distance(a.pos,p.pos)-distance(a.pos,q.pos))[0];
  }
  dropWeapon(weapon:number,pos:Vec,_ammo:number){
    if(!SELECTABLE.includes(weapon)||!allowedWeapon(weapon,this.state.rules))return;
    if(this.state.pickups.length>=48){const oldest=this.state.pickups.find(p=>p.dropped);if(oldest)this.state.pickups=this.state.pickups.filter(p=>p.id!==oldest.id);}
    this.state.pickups.push({id:++this.seq,weapon,pos:{...pos},cooldown:.6,dropped:true,expires:this.state.time+35});
  }
  pickup(a:Actor){
    if(a.dead>0||a.vehicle)return false;const pickup=this.nearestPickup(a);if(!pickup)return false;
    const slot=WEAPONS[pickup.weapon].slot,old=a.inventory[slot];
    if(old!==null&&old!==pickup.weapon)this.dropWeapon(old,a.pos,a.ammo[old]);
    a.inventory[slot]=pickup.weapon;a.weapon=pickup.weapon;a.ammo[pickup.weapon]=WEAPONS[pickup.weapon].mag;a.reload=0;a.cooldown=.25;
    if(pickup.dropped)this.state.pickups=this.state.pickups.filter(p=>p.id!==pickup.id);else pickup.cooldown=20;
    this.event('pickup',pickup.pos,a.id,{weapon:pickup.weapon});return true;
  }
  ai(a:Actor,dt:number):Input {
    const i=emptyInput();i.yaw=a.yaw;i.pitch=a.pitch;i.patch=a.bleed>1||a.hp<40;
    let brain=this.brains.get(a.id);if(!brain){brain=createBotMemory();this.brains.set(a.id,brain);}
    const target=perceive(this.world,this.state.vehicles,a,this.state.actors,brain,this.state.time,this.random);
    let destination:Vec|null=null;
    if(target){
      const dx=target.point.x-a.pos.x,dz=target.point.z-a.pos.z,dist=Math.hypot(dx,dz),desired=Math.atan2(-dx,-dz)+brain.aimOffset;
      const difference=Math.atan2(Math.sin(desired-a.yaw),Math.cos(desired-a.yaw));i.yaw=a.yaw+clamp(difference,-dt*2,dt*2);i.pitch=Math.atan2(target.point.y-eye(a).y,dist);i.ads=dist>20;
      if(this.state.time>=brain.readyAt&&Math.abs(difference)<.1){
        if(this.state.time>=brain.restUntil&&this.state.time>=brain.burstEnd){brain.burstEnd=this.state.time+.4+this.random()*.3;brain.restUntil=brain.burstEnd+.35+this.random()*.4;}
        i.shoot=this.state.time<brain.burstEnd;
      }
      if(dist>18)destination={...target.position};else i.strafe=Math.sin(this.state.time*.8+a.id.length)*.4;
    }else{
      if(brain.lastSeen&&this.state.time-brain.lastSeenAt<2.2&&distance(a.pos,brain.lastSeen)>2)destination={...brain.lastSeen};
      else {
        if(!brain.patrol||distance(a.pos,brain.patrol)<2||this.state.time>brain.patrolUntil){const routes=[v(0,0,-23),v(0,0,23),v(-15,0,-18),v(15,0,18),v(-15,0,15),v(15,0,-15),v(-4,0,-5),v(4,0,9)];brain.patrol=routes[Math.floor(this.random()*routes.length)];brain.patrolUntil=this.state.time+12;}
        destination=brain.patrol;
      }
    }
    if(destination){
      let route=this.aiPaths.get(a.id);if(!route||route.until<this.state.time){route={path:this.path(a.pos,destination),until:this.state.time+1.2};this.aiPaths.set(a.id,route);}
      while(route.path.length&&distance(a.pos,route.path[0])<1.4)route.path.shift();const next=route.path[0];
      if(next){const angle=Math.atan2(-(next.x-a.pos.x),-(next.z-a.pos.z));if(!target){const diff=Math.atan2(Math.sin(angle-a.yaw),Math.cos(angle-a.yaw));i.yaw=a.yaw+clamp(diff,-dt*1.7,dt*1.7);i.pitch*=Math.max(0,1-dt*3);}i.forward=Math.cos(angle-i.yaw);i.strafe=-Math.sin(angle-i.yaw);}
    }
    return i;
  }
'''+s[end:]
p.write_text(s)
