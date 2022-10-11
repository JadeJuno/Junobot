from nbt import nbt


def nbt_to_condition(center: tuple[int, int, int], structure: nbt.NBTFile) -> dict:
	final_condition = {"type": "origins:and", "conditions": []}

	# Turn block pallete to conditions
	pallete = structure['palette']
	conditions_pallete = []
	for state in pallete:
		main_condition = {}
		state = dict(state)
		block_condition = {"type": "origins:block", "block": state['Name'].value}
		if "Properties" in state:
			properties = state['Properties']
			main_condition['type'] = "origins:and"
			main_condition['conditions'] = [
				block_condition
			]
			for tag in properties.tags:
				property_cond = {"type": "origins:block_state", "property": tag.name}
				if tag.value.isdigit():
					property_cond.update({"comparison": "==", "compare_to": int(tag.value)})
				elif tag.value in ("true", "false"):
					property_cond['value'] = tag.value == "true"
				else:
					property_cond['enum'] = tag.value

				main_condition['conditions'].append(property_cond)
		else:
			main_condition = block_condition
		conditions_pallete.append(main_condition)

	# Turn block positions to offset conditions
	blocks = structure['blocks']
	for block in blocks:
		pos = tuple([tag.value for tag in block["pos"]])
		offset = [_pos - _cent for _pos, _cent in zip(pos, center)]
		if offset == [0, 0, 0]:
			offset_condition = conditions_pallete[block['state'].value]
		else:
			offset_condition = {
				"type": "origins:offset",
				"condition": conditions_pallete[block['state'].value],
				"x": offset[0],
				"y": offset[1],
				"z": offset[2]
			}
		final_condition['conditions'].append(offset_condition)

	return final_condition
