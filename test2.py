import yaml
import os

# 定义 .yaml 文件路径
yaml_file_path = os.path.join("./rag", "settings.yaml")

# 读取 YAML 文件中的内容
def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# 更新 YAML 文件内容
def update_yaml_values(config):
    # 修改值
    config['llm']['model'] = 'gpt-4-turbo'  # 更新model的值
    config['parallelization']['stagger'] = 0.5  # 示例更新parallelization
    config['input']['base_dir'] = "new_input_directory"  # 示例更新input路径
    # 可以根据需要继续更新其他值

# 将更新后的内容写回 YAML 文件
def write_yaml_file(file_path, updated_config):
    with open(file_path, 'w') as file:
        yaml.dump(updated_config, file, default_flow_style=False, sort_keys=False)

# 读取现有的 YAML 文件
config = read_yaml_file(yaml_file_path)

# 更新需要更改的值
update_yaml_values(config)

# 将更新后的内容写回 YAML 文件
write_yaml_file(yaml_file_path, config)

print("YAML 文件已更新成功！")
