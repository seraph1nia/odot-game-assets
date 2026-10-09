class_name UIFixtures
extends RefCounted
# Representative authoritative projections, not a gameplay simulator.
static func resources(state: String) -> Dictionary:
	var rows = []
	var names = ["Gold", "Food", "Wood", "Stone", "Metal", "Cloth"]
	var stocks = [24, 15, 8, 4, 12, 0]
	var income = ["+2", "+5", "+1", "0", "+4", "0"]
	if state == "shortage": stocks[1] = 1
	for i in range(6):
		rows.append({"name":names[i], "stock":str(stocks[i]), "income":"0" if state in ["victory", "defeat"] else income[i]})
	return {"title":"P2 · Inspection" if state == "foreign" else "P1 · Your city", "rows":rows,
		"income_heading":"Next turn" if state in ["preparation", "combat"] else "Income/turn",
		"context":"Next building turn.\nNo income on Ready for battle." if state == "preparation" else "Next building turn" if state == "combat" else "Synchronized · disconnected" if state == "lost" else ""}

static func upkeep(state: String) -> Dictionary:
	if state in ["combat", "victory", "defeat"]:
		return {"heading": "Paid this battle · W2" if state == "combat" else "Last battle · W2",
			"rows":[{"label":"Food paid", "value":"6"}, {"label":"Field participants", "value":"6"}], "detail":"Receipt, not the next battle forecast."}
	return {"heading":"Upkeep · Next battle", "rows":[{"label":"Food demand", "value":"6"}, {"label":"Projected payment", "value":"1 food" if state == "shortage" else "6 food"},
		{"label":"Food after payment", "value":"0" if state == "shortage" else "9"}],
		"detail":"5 field soldiers will sit out.\nReady remains available." if state == "shortage" else "Stored units never fight, even when funded."}

static func match_state(state: String) -> Dictionary:
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
