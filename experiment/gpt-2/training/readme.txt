学習の仕方

python train_ft4_seibun_pair_kouzou.py
python train_ft4_seibun_pair_imi.py

python train_ft4_margin_pair.py <マージン>
python train_ft4_margin_imi_pair.py <マージン>


binファイルが作成されるので、rinnaのpytorch_model.binを挿げ替える
python gpt2_valid_all_bin.py <rinnaのdir指定> <ヴァリデーションファイルの指定> <マージン> <エポック>

ヴァリデーション結果を確認
python gpt2_accuracy_all.py <jsonファイルの指定>
総数が一番良いエポックを選択

rinnaのpytorch_model.binを挿げ替える
python gpt2_sentence_all_sh_change-bin.py <rinnaの指定> train-ft4_pair_kouzou_<マージン>-<epoch> <テストファイル>

結果を確認
python gpt2_accuracy_all_csv_2.py <jsonファイルの指定>