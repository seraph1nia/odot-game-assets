class_name UIFixtures
extends RefCounted
# Representative authoritative projections, not a gameplay simulator.
static func skill_tree(points: int = 6) -> Dictionary:
	return {"points":points, "owned":[], "root":{"id":"foundation", "title":"Foundation", "cost":1, "description":"Open three paths. Choose freely between them; all later steps require their parent."}, "branches":[
		{"title":"Vanguard · protection", "nodes":[
			{"id":"guard", "parent":"foundation", "title":"Guard", "cost":1, "description":"Practice a steady defensive stance."},
			{"id":"resolve", "parent":"guard", "title":"Resolve", "cost":1, "description":"Hold your stance under pressure."},
			{"id":"bulwark", "parent":"resolve", "title":"Bulwark", "cost":2, "description":"Anchor the front line for nearby allies."}]},
		{"title":"Wayfinder · precision", "nodes":[
			{"id":"aim", "parent":"foundation", "title":"Aim", "cost":1, "description":"Pick a target with care."},
			{"id":"tempo", "parent":"aim", "title":"Tempo", "cost":1, "description":"Keep a measured rhythm between shots."},
			{"id":"pierce", "parent":"tempo", "title":"Pierce", "cost":2, "description":"Find a gap in a guarded position."}]},
		{"title":"Arcanist · support", "nodes":[
			{"id":"spark", "parent":"foundation", "title":"Spark", "cost":1, "description":"Channel a small pulse of arcane energy."},
			{"id":"ward", "parent":"spark", "title":"Ward", "cost":1, "description":"Shape that energy into a protective ward."},
			{"id":"beacon", "parent":"ward", "title":"Beacon", "cost":2, "description":"Extend the ward as a rallying light."}]}]}
static func resources(state: String) -> Dictionary:
	var rows = []
	var names = ["Gold", "Food", "Wood", "Stone", "Metal", "Cloth"]
	var stocks = [24, 15, 8, 4, 12, 0]
	var income = ["+2", "+5", "+1", "0", "+4", "0"]
	if state == "shortage": stocks[1] = 1
	for i in range(6):
		rows.append({"name":names[i], "stock":str(stocks[i]), "income":"0" if state in ["victory", "defeat", "fallen"] else income[i]})
	return {"title":"P2 · Inspection" if state == "foreign" else "P1 · Your city", "rows":rows,
		"income_heading":"Next turn" if state in ["preparation", "combat"] else "Income/turn",
		"context":"Next building turn.\nNo income on Ready for battle." if state == "preparation" else "Next building turn" if state == "combat" else "Synchronized · disconnected" if state == "lost" else "Fallen owner · no future income; inspection available" if state == "fallen" else "Stale inspection snapshot · not command eligibility" if state == "stale" else ""}

static func upkeep(state: String) -> Dictionary:
	if state in ["combat", "victory", "defeat"]:
		return {"heading": "Paid this battle · W2" if state == "combat" else "Last battle · W2",
			"rows":[{"label":"Food paid", "value":"6"}, {"label":"Field participants", "value":"6"}], "detail":"Receipt, not the next battle forecast."}
	return {"heading":"Upkeep · Next battle", "rows":[{"label":"Food demand", "value":"6"}, {"label":"Projected payment", "value":"1 food" if state == "shortage" else "6 food"},
		{"label":"Food after payment", "value":"0" if state == "shortage" else "9"}],
		"detail":"5 field soldiers will sit out.\nReady remains available." if state == "shortage" else "Stored units never fight, even when funded."}

static func match_state(state: String) -> Dictionary:
	if state == "lobby":
		return {"phase":"Cooperative lobby", "counters":"2 / 4 players · host", "show_ready":false, "show_pause":false, "show_start":true, "can_start":true, "context":"Start request only; the game validates lobby eligibility."}
	var can_edit = state in ["building", "shortage", "preparation"]
	return {"phase":state.capitalize() + " · Wave 2", "counters":"Production 2 of 3" if state != "preparation" else "Income received · Prepare for battle",
		"ready_label":"Ready for battle" if state == "preparation" else "Unready" if state == "ready" else "Ready", "ready_id":"unready" if state == "ready" else "ready", "can_ready":can_edit or state == "ready",
		"pause_label":"Resume whole match" if state == "paused" else "Pause whole match", "pause_id":"resume" if state == "paused" else "pause",
		"can_pause":state not in ["lost", "victory", "defeat"], "terminal":state in ["victory", "defeat"], "show_ready":state != "lost", "show_pause":state != "lost", "show_context":state != "lost",
		"context":"Read-only: another player's city." if state == "foreign" else "No further income." if state in ["victory", "defeat"] else "Shared pause is separate from Settings."}

static func unit(stored: bool = false) -> Dictionary:
	return {"id":101, "name":"Knight", "level":"II", "health_percent":63, "health_text":"34 / 54 HP",
		"profile":"Damage 14 · size 2 · food upkeep 1/battle\nStored reserve" if stored else "Damage 14 · size 2 · food upkeep 1/battle\nField home 1",
		"statuses":"No current statuses" if stored else "▲ Burn · potency 3 · 2.0 simulated seconds\n● Poison ×2 · ◆ Chill 20% · action deadline 130",
		"can_retire":true, "can_send":true, "send_id":"send-field" if stored else "store",
		"send_label":"Send to field" if stored else "Send to Town hall", "reason":"Retirement is permanent, no refund. Storage still owes food.",
		"destinations":[{"id":"field" if stored else "hall-4-generation-2", "label":"Purchased field homes" if stored else "Town hall · plot 4", "available":true},
			{"id":"hall-8-generation-1", "label":"Town hall · plot 8 (full)", "available":false, "reason":"No fitting reserve tile. Existing unit and wounds remain unchanged."}]}

static func roster(stored: bool = false) -> Dictionary:
	var units = []
	for i in range(9 if stored else 18):
		units.append({"id":101+i, "label":"Knight II · #" + str(101+i), "detail":"34/54 HP · size 2 · funded last completed battle" if i == 0 else "54/54 HP · size 2 · no completed funding receipt"})
	return {"title":"Town hall reserves" if stored else "Purchased field homes", "context":"Stored units never deploy automatically; funded survivors may recover on real production." if stored else "Six separate six-size homes; free size in different tiles cannot be pooled.",
		"tiles":["Reserve 1 · 6/6", "Reserve 2 · 6/6", "Reserve 3 · 6/6"] if stored else ["Home 1 · 6/6", "Home 2 · 6/6", "Home 3 · 6/6", "Home 4 · 6/6", "Home 5 · 6/6", "Home 6 · 6/6"], "units":units, "selected_id":101}

# Fixed examples of adapter projections, not rules that advance a match.
static func details(view: String) -> Dictionary:
	var forecast = {"heading":"Upkeep · Next battle", "rows":[{"label":"Food demand", "value":"18"}, {"label":"Projected payment", "value":"1 food"}, {"label":"Food after payment", "value":"0"}], "detail":"17 field soldiers will sit out. Shortage does not disable Ready."}
	var receipt = {"heading":"Paid this battle · W2", "rows":[{"label":"Food paid", "value":"18"}, {"label":"Field participants", "value":"18"}], "detail":"Immutable paid-current-wave receipt, not a next-battle forecast. Stored units never fight."}
	var result = {"sample":view, "title":"City details · P1", "context":"Connected · owner · city 100/100 · army 18\nYou may edit only while unpaused, unready Building/Preparation.",
		"food":[forecast], "reward_heading":"Last shared-clear reward · W1", "reward":"2 gold · 5 food · 1 wood · 1 research point\nProjected snapshot text; no reward/payment logic in UI.",
		"roster":roster(), "allocation_heading":"Enemy allocation", "allocation":"Boneguard II ×3 · deployed\nHooded crossbowman II ×2 · queued\nQueued status: ● Poison ×1 · strength 2 · 3.0 simulated seconds"}
	if view == "paid":
		result.context = "Combat · read-only · paid-current-wave snapshot W2"
		result.food = [receipt]
	elif view == "last":
		receipt.heading = "Last completed battle · W2"
		receipt.rows = [{"label":"Food paid", "value":"1"}, {"label":"Field participants", "value":"1"}, {"label":"Field sit-outs", "value":"17"}]
		receipt.detail = "Last-wave receipt retained separately from the next forecast. Stored reserves never deploy."
		result.food = [forecast, receipt]
		result.reward_heading = "Last shared-clear reward · W2"
		result.allocation = "No active battle. Next-wave allocation is a separate projected snapshot."
	elif view == "fresh":
		result.context = "Fresh session · no completed battle or reward receipt"
		result.food = [{"heading":"Upkeep · No completed battle", "rows":[{"label":"Food demand", "value":"0"}, {"label":"Projected payment", "value":"0 food"}], "detail":"No paid-current-wave or last-wave receipt in this fresh projection."}]
		result.reward_heading = "Shared-clear reward · none"
		result.reward = "No completed shared clear. Nothing carried from the previous session."
		result.roster = {"title":"Purchased field homes", "context":"No units in this fresh projection.", "tiles":[], "units":[]}
		result.allocation = "No queued or deployed enemies in this fresh projection."
	return result

static func hall(view: String) -> Dictionary:
	var reserves = roster(true)
	var profiles = {}
	for row in reserves.units:
		var profile = unit(true)
		profile.id = row.id
		profile.recovery = "Funded survivor · eligible on next real production. No healing applied by UI." if row.id == 101 else "Full health · no recovery needed; no completed funding receipt."
		if row.id != 101: profile.health_percent = 100; profile.health_text = "54 / 54 HP"
		profiles[row.id] = profile
	var storage = {"id":"storage-upgrade", "title":"Storage III · maximum", "quote":"18 size points · 3 separate reserve tiles", "enabled":false, "reason":"Maximum storage level reached."}
	var healing = {"id":"healing-upgrade", "title":"Healing I → II", "quote":"6 gold · 2 wood · 2 stone\n5% → 10% maximum HP/production", "enabled":true, "reason":"Only stored living units funded in the last completed battle recover."}
	var sale = {"id":"sell-hall", "title":"Sell Town hall", "quote":"Investment half-refund", "enabled":false, "variant":"DangerButton", "reason":"Cannot sell an occupied Town hall. Transfer or retire reserves first."}
	var result = {"sample":view, "title":"Town hall · Plot 4", "context":"Storage and healing are independent tracks. Reserve tiles are not battlefield homes.", "storage":storage, "healing":healing, "sale":sale, "roster":reserves, "profiles":profiles, "selected_id":101}
	if view == "empty":
		result.roster = {"title":"Town hall reserves", "context":"Empty reserve tiles; no automatic deployment or recovery.", "tiles":["Reserve 1 · 0/6", "Reserve 2 · 0/6", "Reserve 3 · 0/6"], "units":[]}
		result.profiles = {}
		result.selected_id = -1
		sale.enabled = true
		sale.reason = "Empty hall · adapter permits sale. UI emits intent only."
	elif view == "stale":
		result.context = "Stale selection · hall generation is no longer current. Inspection snapshot only."
		for quote in [storage, healing, sale]: quote.enabled = false; quote.reason = "Stale hall · select a current hall before requesting changes."
		for profile in profiles.values():
			profile.can_send = false
			profile.can_retire = false
			profile.reason = "Stale hall · no command eligibility."
			profile.recovery = "Historical snapshot only; no current recovery eligibility supplied."
	elif view == "storage":
		storage.title = "Storage II → III"
		storage.quote = "12 gold · 2 wood · 3 stone\n12 → 18 size points · adds one separate reserve tile"
		storage.enabled = true
		storage.reason = "Storage upgrade never purchases field homes or healing."
		reserves.tiles = ["Reserve 1 · 6/6", "Reserve 2 · 6/6"]
		reserves.units = reserves.units.slice(0, 6)
		for id in [107, 108, 109]: profiles.erase(id)
	elif view == "recovery":
		profiles[102].health_percent = 63
		profiles[102].health_text = "34 / 54 HP"
		profiles[102].recovery = "Wounded but unfunded last completed battle · not eligible to recover."
		reserves.units[1].detail = "34/54 HP · size 2 · unfunded last completed battle"
		healing.title = "Healing III · maximum"
		healing.quote = "15% maximum HP/real production · independent of storage"
		healing.enabled = false
		healing.reason = "Maximum healing level reached. Eligibility still comes from the adapter."
	elif view == "fragmented":
		reserves.context = "Field free size cannot be pooled across homes; this transfer has no fitting tile."
		for profile in profiles.values():
			profile.destinations = [{"id":"field", "label":"Field homes · no fitting tile", "available":false, "reason":"Free size 1 + 1 in separate field tiles cannot fit this size-two unit."}]
	return result

static func technologies(role: int) -> Array:
	var classes = ["Melee", "Ranged", "Magic"]
	var choices = [["Guardian", "Assault"], ["Venom", "Precision"], ["Fire", "Frost"]]
	var effects = [["Incoming damage reduction 10%", "Direct damage +10%"], ["Poison potency 10%", "Direct damage +10%"], ["Burn potency 20%", "Future action duration +20%"]]
	var master_effects = [["Incoming damage reduction 20%", "Direct damage +20%"], ["Poison potency 15%", "Direct damage +20%"], ["Burn potency 30%", "Future action duration +40%"]]
	var list = [{"id":classes[role].to_lower()+"-foundation", "title":classes[role]+" foundation", "quote":"3 points · maximum HP and direct damage +5%", "enabled":false, "reason":"Owned"}]
	for i in range(2):
		list.append({"id":choices[role][i].to_lower(), "title":choices[role][i], "quote":"6 points · "+effects[role][i], "enabled":true, "reason":"Available. Permanently locks " + choices[role][1-i] + " and its mastery."})
		list.append({"id":choices[role][i].to_lower()+"-mastery", "title":choices[role][i]+" mastery", "quote":"9 points · "+master_effects[role][i]+"; replaces earlier effect", "enabled":false, "reason":"Requires " + choices[role][i] + ". Need 3 more research points."})
	return list
